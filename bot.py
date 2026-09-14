import os
import re
import random
import asyncio
import sys
import subprocess
import urllib.request

# ==========================================
# 🛡️ AUTO-INSTALL MISSING MODULES & FONTS
# ==========================================
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
    import yt_dlp

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InputMediaVideo

FONT_PATH = "font.ttf"

def ensure_font():
    """Downloads a standard fallback TTF font to fix FFmpeg box artifacts on minimal Linux systems."""
    if not os.path.exists(FONT_PATH):
        try:
            url = "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto-Regular.ttf"
            urllib.request.urlretrieve(url, FONT_PATH)
            print("✅ Default TTF font downloaded successfully.")
        except Exception as e:
            print(f"⚠️ Warning: Failed to download font: {e}")

ensure_font()

# ==========================================
# 🛑 CONFIGURATION
# ==========================================
API_ID = 36511364  
API_HASH = "249685fabdef6018e8c84dec25942b91"  
BOT_TOKEN = "8608879552:AAHwDrvWXsBSR2H7E8B-E4gPVOie-052urw"  # Replace with active Bot Token

app = Client("ghost_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# State Storage
user_modes = {}
user_watermarks = {}
media_group_cache = {}

HASHTAGS = "\n\n#viralreels #explorepage #trendingaudio #fashionlookbook #modelaesthetic #4kcontent #foryoupage #outfitinspiration"
CAPTIONS_SET = [
    (
        "POV: You couldn't scroll past this look. 🙈 Rate this look 1 to 10 in the comments! 🖤\n\n"
        "I’ve uploaded the complete 4K unreleased lookbook into my VIP Telegram Server! 🤫✨\n\n"
        "Join VIP for just ₹179 / Month! 💋\n"
        "Link in bio! 👇🖤" + HASHTAGS,
        "Want to video call & chat with me directly? 🙈 Click the link in my bio now! 👇🖤"
    )
]

# ==========================================
# 🎯 HELPER FUNCTIONS
# ==========================================
async def safe_edit(msg, text):
    if not msg: return
    try: await msg.edit_text(text)
    except Exception: pass

async def safe_delete(msg):
    if not msg: return
    try: await msg.delete()
    except Exception: pass

def get_watermark_menu():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("✅ Yes, Add Watermark"), KeyboardButton("❌ No Watermark")]
        ],
        resize_keyboard=True
    )

def get_main_menu():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📸 Image Stealth Wash"), KeyboardButton("🎥 Video Stealth Wash")],
            [KeyboardButton("🔕 Mute & Wash Video"), KeyboardButton("📺 YouTube Stealth Wash")],
            [KeyboardButton("🔗 Insta Link Stealth Wash")]
        ],
        resize_keyboard=True
    )

def build_drawtext_filter(text):
    font_param = f"fontfile='{FONT_PATH}':" if os.path.exists(FONT_PATH) else ""
    return f"drawtext={font_param}text='{text}':x=(w-text_w)/2:y=h-th-40:fontsize=45:fontcolor=white@0.85:shadowcolor=black@0.6:shadowx=2:shadowy=2"

# ==========================================
# 🤖 COMMAND & MENU HANDLERS
# ==========================================
@app.on_message(filters.command(["start", "menu"]))
async def start_cmd(client, message):
    user_id = message.from_user.id
    user_watermarks.setdefault(user_id, True)
    
    await message.reply_text(
        "🤖 **GHOST OPERATOR ACTIVE (V5.0 CLEAN)**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Step 1: Choose Watermark Setting below.\n"
        "Step 2: Select a Stealth Wash mode or send media/Instagram link directly!",
        reply_markup=get_watermark_menu()
    )

@app.on_message(filters.regex(r"^(✅ Yes, Add Watermark|❌ No Watermark)$"))
async def set_watermark(client, message):
    user_id = message.from_user.id
    user_watermarks[user_id] = "Yes" in message.text
    status = "ON 🟢" if user_watermarks[user_id] else "OFF 🔴"
    
    await message.reply_text(
        f"💧 **Watermark Status:** {status}\n\nSelect a processing mode:",
        reply_markup=get_main_menu()
    )

@app.on_message(filters.regex(r"^(📸 Image Stealth Wash|🎥 Video Stealth Wash|🔕 Mute & Wash Video|📺 YouTube Stealth Wash.*|🔗 Insta Link Stealth Wash)$"))
async def set_mode(client, message):
    user_modes[message.from_user.id] = message.text
    await message.reply_text(f"✅ Mode set to: `{message.text}`", reply_markup=get_main_menu())

# ==========================================
# ⚙️ FFMPEG STEALTH ENGINE
# ==========================================
async def process_single_file(client, message_or_path, user_id, mode, apply_wm):
    if isinstance(message_or_path, str):
        file_path = message_or_path
    else:
        file_path = await message_or_path.download(file_name=os.path.join(DOWNLOAD_DIR, f"{user_id}_{random.randint(1000,9999)}"))
        
    ext = file_path.split(".")[-1].lower()
    processed_path = os.path.join(PROCESSED_DIR, f"clean_{user_id}_{random.randint(1000,99999)}.{ext}")

    # Standard ASCII Watermark text definitions (fixes glyph rendering issues)
    if "YouTube" in mode:
        wm_filter = build_drawtext_filter("Professionals Group")
    elif mode == "🔗 Insta Link Stealth Wash":
        wm_filter = build_drawtext_filter("Trusted FF Marketplace")
    else:
        wm_filter = build_drawtext_filter("Alishya Oberoi")

    cmd = ['ffmpeg', '-y', '-i', file_path, '-map_metadata', '-1']

    is_image = ext in ['jpg', 'jpeg', 'png', 'webp']

    if mode == "📸 Image Stealth Wash" or (is_image and mode != "🎥 Video Stealth Wash" and mode != "🔕 Mute & Wash Video"):
        vf = "crop=iw*0.98:ih*0.98,scale=iw:ih,eq=contrast=1.02:brightness=0.01,noise=alls=1:allf=t+u"
        if apply_wm: vf += f",{wm_filter}"
        cmd.extend(['-vf', vf, '-q:v', '2', processed_path])

    elif mode == "🎥 Video Stealth Wash":
        vf = "crop=iw*0.98:ih*0.98,scale=iw:ih,eq=contrast=1.03:brightness=0.01,noise=alls=1:allf=t+u,setpts=1/1.05*PTS"
        if apply_wm: vf += f",{wm_filter}"
        cmd.extend(['-vf', vf, '-af', 'atempo=1.05', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', processed_path])

    elif mode == "🔕 Mute & Wash Video":
        vf = "crop=iw*0.98:ih*0.98,scale=iw:ih,eq=contrast=1.03:brightness=0.01,noise=alls=1:allf=t+u,setpts=1/1.05*PTS"
        if apply_wm: vf += f",{wm_filter}"
        cmd.extend(['-vf', vf, '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', processed_path])

    elif "YouTube Stealth Wash" in mode:
        vf = "crop=iw*0.95:ih*0.95,scale=iw:ih,eq=contrast=1.05:brightness=0.02:saturation=1.07,noise=alls=1:allf=t+u,setpts=1/1.04*PTS"
        if apply_wm: vf += f",{wm_filter}"
        cmd.extend(['-vf', vf, '-af', 'atempo=1.04,asetrate=44100*1.01', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', processed_path])

    else:
        vf = "crop=iw*0.98:ih*0.98,scale=iw:ih,eq=contrast=1.03:brightness=0.01,noise=alls=1:allf=t+u,setpts=1/1.05*PTS"
        if apply_wm: vf += f",{wm_filter}"
        cmd.extend(['-vf', vf, '-af', 'atempo=1.05', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', processed_path])

    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await process.communicate()
    
    if os.path.exists(file_path): os.remove(file_path)
    return processed_path

# ==========================================
# 📦 TELEGRAM ALBUM PROCESSOR
# ==========================================
async def process_album_task(client, original_message, mg_id, user_id, mode, apply_wm):
    await asyncio.sleep(3)
    messages = media_group_cache.pop(mg_id, [])
    if not messages: return

    status_msg = await original_message.reply_text(f"⏳ Processing Album ({len(messages)} items)...")
    processed_files = []
    media_group_to_send = []

    try:
        for msg in messages:
            out_path = await process_single_file(client, msg, user_id, mode, apply_wm)
            processed_files.append(out_path)
            ext = out_path.split(".")[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                media_group_to_send.append(InputMediaPhoto(media=out_path))
            else:
                media_group_to_send.append(InputMediaVideo(media=out_path))

        # Send in chunks of 10 if necessary
        for i in range(0, len(media_group_to_send), 10):
            await client.send_media_group(chat_id=user_id, media=media_group_to_send[i:i+10])
        
        selected_caption, _ = random.choice(CAPTIONS_SET)
        await original_message.reply_text(f"📝 **CAPTION:**\n`{selected_caption}`")
        await safe_delete(status_msg)

    except Exception as e:
        await safe_edit(status_msg, f"❌ Album Processing Error: {str(e)}")
    finally:
        for p in processed_files:
            if os.path.exists(p): os.remove(p)

# ==========================================
# 📸 INSTAGRAM EXTRACTION ENGINE
# ==========================================
def fetch_insta_post(url, download_folder):
    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(id)s_%(autonumber)02d.%(ext)s'),
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'extract_flat': False,
        'allow_playlist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    caption = ""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry and (entry.get('description') or entry.get('title')):
                        caption = entry.get('description') or entry.get('title')
                        break
            if not caption:
                caption = info.get('description') or info.get('title') or ""
    return caption

# ==========================================
# 💬 MESSAGE HANDLERS
# ==========================================
@app.on_message(filters.text & ~filters.command(["start", "menu"]))
async def handle_text_messages(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text in [
        "📸 Image Stealth Wash", "🎥 Video Stealth Wash", "🔕 Mute & Wash Video", 
        "📺 YouTube Stealth Wash", "🔗 Insta Link Stealth Wash", 
        "✅ Yes, Add Watermark", "❌ No Watermark"
    ]:
        return

    # Auto-Detect Instagram Links
    if "instagram.com" in text or "instagr.am" in text:
        user_modes[user_id] = "🔗 Insta Link Stealth Wash"
        user_watermarks.setdefault(user_id, True)

        urls = re.findall(r'https?://[^\s]+', text)
        url = urls[0] if urls else text
        apply_wm = user_watermarks[user_id]

        status_msg = await message.reply_text("📥 Extracting Instagram media...")
        task_dir = os.path.join(DOWNLOAD_DIR, f"insta_{user_id}_{random.randint(1000,9999)}")
        os.makedirs(task_dir, exist_ok=True)

        try:
            caption = await asyncio.to_thread(fetch_insta_post, url, task_dir)
            downloaded_files = sorted([
                os.path.join(task_dir, f) for f in os.listdir(task_dir) 
                if os.path.isfile(os.path.join(task_dir, f))
            ])

            if not downloaded_files:
                await safe_edit(status_msg, "❌ Could not extract media. Ensure post is public or try again.")
                return

            await safe_edit(status_msg, f"🔄 Washing {len(downloaded_files)} extracted file(s)...")

            processed_files = []
            media_group_to_send = []

            for fpath in downloaded_files:
                out_path = await process_single_file(client, fpath, user_id, "🔗 Insta Link Stealth Wash", apply_wm)
                processed_files.append(out_path)
                
                ext = out_path.split(".")[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    media_group_to_send.append(InputMediaPhoto(media=out_path))
                else:
                    media_group_to_send.append(InputMediaVideo(media=out_path))

            if len(media_group_to_send) == 1:
                item = media_group_to_send[0]
                if isinstance(item, InputMediaPhoto):
                    await message.reply_photo(photo=item.media)
                else:
                    await message.reply_video(video=item.media, supports_streaming=True)
            else:
                for i in range(0, len(media_group_to_send), 10):
                    await client.send_media_group(chat_id=user_id, media=media_group_to_send[i:i+10])

            await safe_delete(status_msg)

            # Preserves original extracted Instagram caption if present
            final_caption = f"{caption.strip()}\n{HASHTAGS}" if caption else HASHTAGS.strip()
            await message.reply_text(f"📝 **CAPTION:**\n`{final_caption}`")

        except Exception as e:
            await safe_edit(status_msg, f"❌ Processing Error: {str(e)}")

        finally:
            if os.path.exists(task_dir):
                for f in os.listdir(task_dir):
                    try: os.remove(os.path.join(task_dir, f))
                    except Exception: pass
                try: os.rmdir(task_dir)
                except Exception: pass

@app.on_message(filters.photo | filters.video | filters.document)
async def handle_media(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_modes:
        user_modes[user_id] = "📸 Image Stealth Wash" if message.photo else "🎥 Video Stealth Wash"
    if user_id not in user_watermarks:
        user_watermarks[user_id] = True

    mode = user_modes[user_id]
    apply_wm = user_watermarks[user_id]

    if message.media_group_id:
        mg_id = message.media_group_id
        if mg_id not in media_group_cache:
            media_group_cache[mg_id] = []
            asyncio.create_task(process_album_task(client, message, mg_id, user_id, mode, apply_wm))
        media_group_cache[mg_id].append(message)
        return

    status_msg = await message.reply_text("🔄 Processing media...")

    try:
        processed_path = await process_single_file(client, message, user_id, mode, apply_wm)
        ext = processed_path.split(".")[-1].lower()

        if ext in ['jpg', 'jpeg', 'png', 'webp']:
            await message.reply_photo(photo=processed_path)
        else:
            await message.reply_video(video=processed_path, supports_streaming=True)

        await safe_delete(status_msg)

        selected_caption, _ = random.choice(CAPTIONS_SET)
        await message.reply_text(f"📝 **CAPTION:**\n`{selected_caption}`")

    except Exception as e:
        await safe_edit(status_msg, f"❌ Error: {str(e)}")
    finally:
        if 'processed_path' in locals() and os.path.exists(processed_path):
            os.remove(processed_path)

if __name__ == "__main__":
    print("🚀 Clean Ghost Operator Active (V5.0 Clean)...")
    app.run()
