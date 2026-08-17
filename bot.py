import os
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton

API_ID = 36511364  
API_HASH = "249685fabdef6018e8c84dec25942b91"  
BOT_TOKEN = "8608879552:AAHwDrvWXsBSR2H7E8B-E4gPVOie-052urw"  

app = Client(
    "ghost_session", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN
)

DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

user_modes = {}

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
        "System secure. Meta & YouTube AI bypass pipeline active.\n\n"
        "Choose an option below and send your asset.",
        reply_markup=get_main_menu()
    )

@app.on_message(filters.regex(r"^(📸 Image Stealth Wash|🎥 Video Stealth Wash|🔕 Mute & Wash Video|📺 YouTube Stealth Wash \(20\+ Min\))$"))
async def set_mode(client, message):
    user_modes[message.from_user.id] = message.text
    await message.reply_text(
        f"✅ **Mode Selected:** `{message.text}`\n\nNow send your raw file directly here!",
        reply_markup=get_main_menu()
    )

@app.on_message(filters.photo | filters.video | filters.document)
async def handle_media(client, message):
    user_id = message.from_user.id
    if user_id not in user_modes:
        await message.reply_text("⚠️ Please select a mode from the menu first!")
        return

    mode = user_modes[user_id]
    processing_msg = await message.reply_text("📥 **Downloading asset... (Up to 2GB)**")

    try:
        file_path = await message.download(file_name=DOWNLOAD_DIR + "/")
        await processing_msg.edit_text("🔄 **Executing Advanced FFmpeg AI Bypass...**")

        ext = file_path.split(".")[-1].lower()
        processed_path = os.path.join(PROCESSED_DIR, f"clean_{user_id}_{random.randint(1000,9999)}.{ext}")

        if mode == "📸 Image Stealth Wash":
            vf = "hflip,drawtext=text='Alishya Oberoi':x=(w-text_w)/2:y=h-th-40:fontsize=36:fontcolor=white@0.7"
            cmd = ['ffmpeg', '-y', '-i', file_path, '-vf', vf, '-q:v', '2', processed_path]
        
        elif mode == "🎥 Video Stealth Wash":
            vf = "hflip,setpts=1/1.08*PTS,drawtext=text='Alishya Oberoi':x=(w-text_w)/2:y=h-th-40:fontsize=36:fontcolor=white@0.7"
            cmd = ['ffmpeg', '-y', '-i', file_path, '-vf', vf, '-af', 'atempo=1.08', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', processed_path]

        elif mode == "🔕 Mute & Wash Video":
            vf = "hflip,setpts=1/1.08*PTS,drawtext=text='Alishya Oberoi':x=(w-text_w)/2:y=h-th-40:fontsize=36:fontcolor=white@0.7"
            cmd = ['ffmpeg', '-y', '-i', file_path, '-vf', vf, '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', processed_path]

        elif mode == "📺 YouTube Stealth Wash (20+ Min)":
            vf = "crop=iw*0.95:ih*0.95,scale=iw:ih,hflip,eq=contrast=1.04:brightness=0.02:saturation=1.05,setpts=1/1.08*PTS,drawtext=text='Professionals Group':x=(w-text_w)/2:y=h-th-50:fontsize=42:fontcolor=white@0.7"
            cmd = ['ffmpeg', '-y', '-i', file_path, '-vf', vf, '-af', 'atempo=1.08', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', processed_path]

        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await process.communicate()

        await processing_msg.edit_text("📤 **Uploading washed asset to Telegram...**")

        if mode == "📸 Image Stealth Wash":
            await message.reply_photo(photo=processed_path)
        else:
            await message.reply_video(video=processed_path, supports_streaming=True)

        await processing_msg.delete()

        selected_caption, selected_pinned = random.choice(CAPTIONS_SET)
        await message.reply_text(f"📝 **1-TAP COPY CAPTION:**\n`{selected_caption}`")
        await message.reply_text(f"💬 **1-TAP COPY PINNED COMMENT:**\n`{selected_pinned}`")

    except Exception as e:
        await processing_msg.edit_text(f"❌ **Error:** {str(e)}")

    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        if 'processed_path' in locals() and os.path.exists(processed_path):
            os.remove(processed_path)

if __name__ == "__main__":
    print("🚀 Ghost Operator Pyrogram Engine is Running on Cloud...")
    app.run()
