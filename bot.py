import os
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InputMediaVideo

# ==========================================
# 🛑 PASTE YOUR NEW BOT TOKEN BELOW
# ==========================================
API_ID = 36511364  
API_HASH = "249685fabdef6018e8c84dec25942b91"  
BOT_TOKEN = "8608879552:AAHwDrvWXsBSR2H7E8B-E4gPVOie-052urw"  # <-- Naya token yahan!

app = Client("ghost_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app.no_updates = False

DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

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

def get_watermark_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("✅ Yes, Add Watermark"), KeyboardButton("❌ No Watermark")]],
        resize_keyboard=True
    )

def get_main_menu():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📸 Image Stealth Wash")],
            [KeyboardButton("🎥 Video Stealth Wash"), KeyboardButton("🔕 Mute & Wash Video")],
            [KeyboardButton("📺 YouTube Stealth Wash (20+ Min)")]
        ],
        resize_keyboard=True
    )

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text(
        "🤖 **GHOST OPERATOR ACTIVE**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Do you want to add the Crystal Watermark on your files?",
        reply_markup=get_watermark_menu()
    )

@app.on_message(filters.regex(r"^(✅ Yes, Add Watermark|❌ No Watermark)$"))
async def set_watermark(client, message):
    user_id = message.from_user.id
    user_watermarks[user_id] = True if "Yes" in message.text else False
    
    status = "ON 🟢" if user_watermarks[user_id] else "OFF 🔴"
    await message.reply_text(
        f"💧 **Watermark Status:** {status}\nI will remember this! Now choose a processing mode below:",
        reply_markup=get_main_menu()
    )

@app.on_message(filters.regex(r"^(📸 Image Stealth Wash|🎥 Video Stealth Wash|🔕 Mute & Wash Video|📺 YouTube Stealth Wash \(20\+ Min\))$"))
async def set_mode(client, message):
    user_modes[message.from_user.id] = message.text
    await message.reply_text(
        f"✅ **Mode Selected:** `{message.text}`\n\nSend your file(s) or an entire Album directly here!",
        reply_markup=get_main_menu()
    )

async def process_single_file(client, message, user_id, mode, apply_wm):
    file_path = await message.download(file_name=DOWNLOAD_DIR + "/")
    ext = file_path.split(".")[-1].lower()
    processed_path = os.path.join(PROCESSED_DIR, f"clean_{user_id}_{random.randint(1000,99999)}.{ext}")

    wm_alishya = "drawtext=text='𝘼𝙡𝙞𝙨𝙝𝙮𝙖 𝙊𝙗𝙚𝙧𝙤𝙞':x=(w-text_w)/2:y=h-th-40:fontsize=45:fontcolor=white@0.85:shadowcolor=black@0.6:shadowx=2:shadowy=2"
    wm_prof = "drawtext=text='𝐏𝐫𝐨𝐟𝐞𝐬𝐬𝐢𝐨𝐧𝐚𝐥𝐬 𝐆𝐫𝐨𝐮𝐩':x=(w-text_w)/2:y=h-th-50:fontsize=55:fontcolor=white@0.9:shadowcolor=black@0.8:shadowx=3:shadowy=3:borderw=1:bordercolor=white@0.3"

    cmd = ['ffmpeg', '-y', '-i', file_path, '-map_metadata', '-1']

    if mode == "📸 Image Stealth Wash":
        vf = "crop=iw*0.98:ih*0.98,scale=iw:ih,eq=contrast=1.02:brightness=0.01,noise=alls=1:allf=t+u"
        if apply_wm: vf += f",{wm_alishya}"
        cmd.extend(['-vf', vf, '-q:v', '2', processed_path])
    
    elif mode == "🎥 Video Stealth Wash":
        vf = "crop=iw*0.98:ih*0.98,scale=iw:ih,eq=contrast=1.03:brightness=0.01,noise=alls=1:allf=t+u,setpts=1/1.05*PTS"
        if apply_wm: vf += f",{wm_alishya}"
        cmd.extend(['-vf', vf, '-af', 'atempo=1.05', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', processed_path])

    elif mode == "🔕 Mute & Wash Video":
        vf = "crop=iw*0.98:ih*0.98,scale=iw:ih,eq=contrast=1.03:brightness=0.01,noise=alls=1:allf=t+u,setpts=1/1.05*PTS"
        if apply_wm: vf += f",{wm_alishya}"
        cmd.extend(['-vf', vf, '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', processed_path])

    elif mode == "📺 YouTube Stealth Wash (20+ Min)":
        vf = "crop=iw*0.95:ih*0.95,scale=iw:ih,eq=contrast=1.05:brightness=0.02:saturation=1.07,noise=alls=1:allf=t+u,setpts=1/1.04*PTS"
        if apply_wm: vf += f",{wm_prof}"
        cmd.extend(['-vf', vf, '-af', 'atempo=1.04,asetrate=44100*1.01', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', processed_path])

    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await process.communicate()
    
    if os.path.exists(file_path): os.remove(file_path)
    return processed_path

async def process_album_task(client, original_message, mg_id, user_id, mode, apply_wm):
    await asyncio.sleep(5)
    messages = media_group_cache.pop(mg_id, [])
    if not messages: return

    status_msg = None
    try:
        status_msg = await original_message.reply_text(f"📚 **Album Detected!** Processing {len(messages)} files together. Please wait...")
    except Exception:
        pass
    
    processed_files = []
    media_group_to_send = []

    try:
        for msg in messages:
            out_path = await process_single_file(client, msg, user_id, mode, apply_wm)
            processed_files.append(out_path)
            
            if mode == "📸 Image Stealth Wash":
                media_group_to_send.append(InputMediaPhoto(media=out_path))
            else:
                media_group_to_send.append(InputMediaVideo(media=out_path))

        if status_msg:
            try:
                await status_msg.edit_text("📤 **Uploading your Album...**")
            except Exception:
                pass

        await client.send_media_group(chat_id=user_id, media=media_group_to_send)
        
        selected_caption, selected_pinned = random.choice(CAPTIONS_SET)
        await original_message.reply_text(f"📝 **1-TAP COPY CAPTION FOR ALBUM:**\n`{selected_caption}`")
        await original_message.reply_text(f"💬 **1-TAP COPY PINNED COMMENT:**\n`{selected_pinned}`")
        
        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass

    except Exception as e:
        await original_message.reply_text(f"❌ **Album Error:** {str(e)}")
    
    finally:
        for p in processed_files:
            if os.path.exists(p): os.remove(p)

@app.on_message(filters.photo | filters.video | filters.document)
async def handle_media(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_modes:
        await message.reply_text("⚠️ Please select a mode from the menu first!")
        return
    if user_id not in user_watermarks:
        await message.reply_text("⚠️ Please select Watermark Yes/No from the /start menu first!")
        return

    mode = user_modes[user_id]
    apply_wm = user_watermarks[user_id]

    if message.media_group_id:
        mg_id = message.media_group_id
        if mg_id not in media_group_cache:
            media_group_cache[mg_id] = []
            asyncio.create_task(process_album_task(client, message, mg_id, user_id, mode, apply_wm))
        media_group_cache[mg_id].append(message)
        return

    processing_msg = None
    try:
        processing_msg = await message.reply_text("📥 **Downloading single asset...**")
    except Exception:
        pass

    try:
        if processing_msg:
            try:
                await processing_msg.edit_text("🔄 **Executing Advanced AI Stealth Bypass...**")
            except Exception:
                pass

        processed_path = await process_single_file(client, message, user_id, mode, apply_wm)
        
        if processing_msg:
            try:
                await processing_msg.edit_text("📤 **Uploading washed asset...**")
            except Exception:
                pass

        if mode == "📸 Image Stealth Wash":
            await message.reply_photo(photo=processed_path)
        else:
            await message.reply_video(video=processed_path, supports_streaming=True)

        if processing_msg:
            try:
                await processing_msg.delete()
            except Exception:
                pass

        selected_caption, selected_pinned = random.choice(CAPTIONS_SET)
        await message.reply_text(f"📝 **1-TAP COPY CAPTION:**\n`{selected_caption}`")
        await message.reply_text(f"💬 **1-TAP COPY PINNED COMMENT:**\n`{selected_pinned}`")

        if os.path.exists(processed_path): os.remove(processed_path)

    except Exception as e:
        if processing_msg:
            try:
                await processing_msg.edit_text(f"❌ **Error:** {str(e)}")
            except Exception:
                await message.reply_text(f"❌ **Error:** {str(e)}")
        else:
            await message.reply_text(f"❌ **Error:** {str(e)}")

if __name__ == "__main__":
    print("🚀 Ultimate Stealth Pipeline Active...")
    app.run()
