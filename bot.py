import os
import re
import random
import asyncio
import sys
import subprocess
import urllib.request

# ==========================================
# 🛡️ AUTO-INSTALL MISSING MODULES
# ==========================================
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InputMediaVideo

# ==========================================
# 🛑 PASTE YOUR BOT TOKEN BELOW
# ==========================================
API_ID = 36511364
API_HASH = "249685fabdef6018e8c84dec25942b91"
BOT_TOKEN = "8608879552:AAHwDrvWXsBSR2H7E8B-E4gPVOie-052urw"  # <-- Naya token yahan!

app = Client("ghost_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
FONT_FILE = "DejaVuSans.ttf"
FONT_URL = "https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37/ttf/DejaVuSans.ttf"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ==========================================
# 🔤 AUTO-DOWNLOAD TRUETYPE FONT (Fix □□□)
# ==========================================
def ensure_font():
    if not os.path.exists(FONT_FILE):
        print(f"⬇️ Downloading font: {FONT_FILE} ...")
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_FILE)
            print(f"✅ Font ready: {FONT_FILE}")
        except Exception as e:
            print(f"⚠️ Font download failed: {e}")
    else:
        print(f"✅ Font already present: {FONT_FILE}")

ensure_font()

# Memory Dictionaries
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

async def safe_edit(msg, text):
    if not msg:
        return
    try:
        await msg.edit_text(text)
    except Exception:
        pass

async def safe_delete(msg):
    if not msg:
        return
    try:
        await msg.delete()
    except Exception:
        pass

def get_watermark_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("✅ Yes, Add Watermark"), KeyboardButton("❌ No Watermark")]],
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

@app.on_message(filters.command(["start", "menu"]))
async def start_cmd(client, message):
    await message.reply_text(
        "🤖 **GHOST OPERATOR ACTIVE (V6.0 PRODUCTION)**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Send any media or Instagram link directly!\n"
        "All media is auto-stealth-washed + re-branded.",
        reply_markup=get_main_menu()
    )

@app.on_message(filters.regex(r"^(✅ Yes, Add Watermark|❌ No Watermark)$"))
async def set_watermark(client, message):
    user_id = message.from_user.id
    user_watermarks[user_id] = True if "Yes" in message.text else False
    status = "ON 🟢" if user_watermarks[user_id] else "OFF 🔴"
    await message.reply_text(f"💧 **Watermark:** {status}", reply_markup=get_main_menu())

@app.on_message(filters.regex(r"^(📸 Image Stealth Wash|🎥 Video Stealth Wash|🔕 Mute & Wash Video|📺 YouTube Stealth Wash.*|🔗 Insta Link Stealth Wash)$"))
async def set_mode(client, message):
    user_modes[message.from_user.id] = message.text
    await message.reply_text(f"✅ Mode: `{message.text}`", reply_markup=get_main_menu())

def build_delogo_filters():
    filters = [
        "delogo=x=10:y=10:w=180:h=60:show=0",
        "delogo=x=w-190:y=10:w=180:h=60:show=0",
        "delogo=x=10:y=h-70:w=180:h=60:show=0",
        "delogo=x=w-190:y=h-70:w=180:h=60:show=0",
        "delogo=x=(w-220)/2:y=h-80:w=220:h=70:show=0",
    ]
    return ",".join(filters)

def get_watermark_text(mode: str) -> str:
    if "YouTube" in mode:
        return "Professionals Group"
    elif "Insta" in mode:
        return "Trusted FF Marketplace"
    else:
        return "Alishya Oberoi"

async def process_single_file(client, message_or_path, user_id, mode, apply_wm):
    if isinstance(message_or_path, str):
        file_path = message_or_path
    else:
        file_path = await message_or_path.download(file_name=os.path.join(DOWNLOAD_DIR, ""))

    ext = file_path.split(".")[-1].lower()
    processed_path = os.path.join(PROCESSED_DIR, f"clean_{user_id}_{random.randint(10000, 99999)}.{ext}")

    delogo = build_delogo_filters()
    font_param = f"fontfile='{FONT_FILE}'" if os.path.exists(FONT_FILE) else ""

    if mode == "📸 Image Stealth Wash" or (ext in ["jpg", "jpeg", "png", "webp"] and "Insta" in mode):
        base_vf = (
            f"{delogo},"
            "crop=iw*0.98:ih*0.98,"
            "scale=iw:ih,"
            "eq=contrast=1.02:brightness=0.01,"
            "noise=alls=1:allf=t+u"
        )
        if apply_wm:
            wm_text = get_watermark_text(mode)
            base_vf += (
                f",drawtext=text='{wm_text}':"
                f"{font_param}:"
                "x=(w-text_w)/2:y=h-th-40:"
                "fontsize=42:fontcolor=white@0.88:"
                "shadowcolor=black@0.65:shadowx=2:shadowy=2:"
                "borderw=1:bordercolor=black@0.3"
            )
        cmd = [
            "ffmpeg", "-y", "-i", file_path,
            "-map_metadata", "-1",
            "-vf", base_vf,
            "-q:v", "2",
            processed_path
        ]
    else:
        speed = 1.05
        if "YouTube" in mode:
            speed = 1.04
            contrast = "1.05"
            brightness = "0.02"
            saturation = "1.07"
            crop_factor = "0.95"
            crf = "20"
            preset = "medium"
        else:
            contrast = "1.03"
            brightness = "0.01"
            saturation = "1.0"
            crop_factor = "0.98"
            crf = "18"
            preset = "fast"

        base_vf = (
            f"{delogo},"
            f"crop=iw*{crop_factor}:ih*{crop_factor},"
            "scale=iw:ih,"
            f"eq=contrast={contrast}:brightness={brightness}:saturation={saturation},"
            "noise=alls=1:allf=t+u,"
            f"setpts=1/{speed}*PTS"
        )

        if apply_wm:
            wm_text = get_watermark_text(mode)
            base_vf += (
                f",drawtext=text='{wm_text}':"
                f"{font_param}:"
                "x=(w-text_w)/2:y=h-th-45:"
                "fontsize=48:fontcolor=white@0.90:"
                "shadowcolor=black@0.7:shadowx=3:shadowy=3:"
                "borderw=1:bordercolor=white@0.25"
            )

        cmd = [
            "ffmpeg", "-y", "-i", file_path,
            "-map_metadata", "-1",
            "-vf", base_vf,
        ]

        if mode == "🔕 Mute & Wash Video":
            cmd.extend(["-an"])
        else:
            audio_filter = f"atempo={speed}"
            if "YouTube" in mode:
                audio_filter = f"atempo={speed},asetrate=44100*1.01"
            cmd.extend(["-af", audio_filter, "-c:a", "aac"])

        cmd.extend([
            "-c:v", "libx264",
            "-crf", crf,
            "-preset", preset,
            "-movflags", "+faststart",
            processed_path
        ])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        err_msg = stderr.decode()[-500:] if stderr else "Unknown FFmpeg error"
        raise RuntimeError(f"FFmpeg failed: {err_msg}")

    if os.path.exists(file_path) and file_path.startswith(DOWNLOAD_DIR):
        try:
            os.remove(file_path)
        except Exception:
            pass

    return processed_path

async def process_album_task(client, original_message, mg_id, user_id, mode, apply_wm):
    await asyncio.sleep(3.5)
    messages = media_group_cache.pop(mg_id, [])
    if not messages:
        return

    status_msg = await original_message.reply_text(f"⏳ Processing Album ({len(messages)} files)...")
    processed_files = []
    media_group_to_send = []

    try:
        for msg in messages:
            out_path = await process_single_file(client, msg, user_id, mode, apply_wm)
            processed_files.append(out_path)
            ext = out_path.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "webp"]:
                media_group_to_send.append(InputMediaPhoto(media=out_path))
            else:
                media_group_to_send.append(InputMediaVideo(media=out_path, supports_streaming=True))

        await client.send_media_group(chat_id=user_id, media=media_group_to_send)

        selected_caption, _ = random.choice(CAPTIONS_SET)
        await original_message.reply_text(f"📝 **CAPTION:**\n`{selected_caption}`")
        await safe_delete(status_msg)

    except Exception as e:
        await safe_edit(status_msg, f"❌ Error: {str(e)[:300]}")
    finally:
        for p in processed_files:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

def fetch_insta_post(url, download_folder):
    ydl_opts = {
        "outtmpl": os.path.join(download_folder, "%(id)s_%(autonumber)02d.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "extract_flat": False,
        "format": "best",
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.instagram.com/",
            "Origin": "https://www.instagram.com",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            return ""
        caption = info.get("description") or info.get("title") or ""
        return caption.strip()

@app.on_message(filters.text & \~filters.command(["start", "menu"]))
async def handle_text_messages(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text in [
        "📸 Image Stealth Wash", "🎥 Video Stealth Wash", "🔕 Mute & Wash Video",
        "📺 YouTube Stealth Wash", "🔗 Insta Link Stealth Wash",
        "✅ Yes, Add Watermark", "❌ No Watermark"
    ]:
        return

    if "instagram.com" in text or "instagr.am" in text:
        user_modes[user_id] = "🔗 Insta Link Stealth Wash"
        user_watermarks.setdefault(user_id, True)

        urls = re.findall(r"https?://[^\s]+", text)
        url = urls[0] if urls else text
        apply_wm = user_watermarks.get(user_id, True)

        status_msg = await message.reply_text("📥 Fetching Instagram Post / Reel / Carousel...")
        task_dir = os.path.join(DOWNLOAD_DIR, f"insta_{user_id}_{random.randint(1000, 9999)}")
        os.makedirs(task_dir, exist_ok=True)

        processed_files = []
        try:
            caption = await asyncio.to_thread(fetch_insta_post, url, task_dir)
            downloaded_files = sorted([
                os.path.join(task_dir, f)
                for f in os.listdir(task_dir)
                if os.path.isfile(os.path.join(task_dir, f))
                and not f.endswith((".json", ".description", ".info.json"))
            ])

            if not downloaded_files:
                await safe_edit(status_msg, "❌ Could not extract media. Post may be private or restricted.")
                return

            await safe_edit(status_msg, f"🔄 Processing {len(downloaded_files)} file(s) with full stealth wash...")

            media_group_to_send = []

            for fpath in downloaded_files:
                out_path = await process_single_file(
                    client, fpath, user_id, "🔗 Insta Link Stealth Wash", apply_wm
                )
                processed_files.append(out_path)

                ext = out_path.split(".")[-1].lower()
                if ext in ["jpg", "jpeg", "png", "webp"]:
                    media_group_to_send.append(InputMediaPhoto(media=out_path))
                else:
                    media_group_to_send.append(
                        InputMediaVideo(media=out_path, supports_streaming=True)
                    )

            if len(media_group_to_send) == 1:
                item = media_group_to_send[0]
                if isinstance(item, InputMediaPhoto):
                    await message.reply_photo(photo=item.media)
                else:
                    await message.reply_video(video=item.media, supports_streaming=True)
            else:
                await client.send_media_group(chat_id=user_id, media=media_group_to_send)

            await safe_delete(status_msg)

            final_caption = f"{caption}\n\n{HASHTAGS}" if caption else HASHTAGS
            await message.reply_text(f"📝 **CAPTION:**\n`{final_caption}`")

        except Exception as e:
            await safe_edit(status_msg, f"❌ Error: {str(e)[:350]}")
        finally:
            if os.path.exists(task_dir):
                for f in os.listdir(task_dir):
                    try:
                        os.remove(os.path.join(task_dir, f))
                    except Exception:
                        pass
                try:
                    os.rmdir(task_dir)
                except Exception:
                    pass
            for p in processed_files:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

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
            asyncio.create_task(
                process_album_task(client, message, mg_id, user_id, mode, apply_wm)
            )
        media_group_cache[mg_id].append(message)
        return

    status_msg = await message.reply_text("🔄 Processing media with stealth wash...")

    try:
        processed_path = await process_single_file(client, message, user_id, mode, apply_wm)

        if mode == "📸 Image Stealth Wash" or processed_path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            await message.reply_photo(photo=processed_path)
        else:
            await message.reply_video(video=processed_path, supports_streaming=True)

        await safe_delete(status_msg)

        selected_caption, _ = random.choice(CAPTIONS_SET)
        await message.reply_text(f"📝 **CAPTION:**\n`{selected_caption}`")

        if os.path.exists(processed_path):
            os.remove(processed_path)

    except Exception as e:
        await safe_edit(status_msg, f"❌ Error: {str(e)[:300]}")

if __name__ == "__main__":
    print("🚀 Clean Ghost Operator V6.0 (Production) Active...")
    print(f"🔤 Font status: {'READY' if os.path.exists(FONT_FILE) else 'MISSING'}")
    app.run()
