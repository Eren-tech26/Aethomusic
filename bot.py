import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
from config import API_ID, API_HASH, BOT_TOKEN

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store current playing info
current_queue = []
is_playing = False

def search_youtube(query):
    """Search YouTube for a song using yt-dlp"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info and 'entries' in info:
                return info['entries'][0]
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
    return None

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    """Start command with image and buttons"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▶️ ᴘʟᴀʏ", callback_data="play_music"),
            InlineKeyboardButton("📝 ᴄᴏᴍᴍᴀɴᴅs", callback_data="commands")
        ],
        [
            InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton("🛠️ ᴍᴏᴅᴜʟᴇs", callback_data="modules")
        ],
        [
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/aethosupport")
        ],
        [
            InlineKeyboardButton("🔗 ɴᴇᴛᴡᴏʀᴋ", url="https://t.me/Aethonix_network")
        ]
    ])
    
    await message.reply_photo(
        photo="https://ibb.co/9mKvy2dM",
        caption=
            "🎵 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ! 🎵\n\n"
            "ᴘʟᴀʏ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ sᴏɴɢs ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ɪɴ ᴛᴇʟᴇɢʀᴀᴍ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs!\n\n"
            "ᴜsᴇ /ᴘʟᴀʏ [sᴏɴɢ ɴᴀᴍᴇ] ᴛᴏ sᴛᴀʀᴛ ᴘʟᴀʏɪɴɢ ᴍᴜsɪᴄ.\n\n"
            "ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴇxᴘʟᴏʀᴇ!",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("play_music"))
async def play_music_callback(client, callback_query):
    """Callback for play music button"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback_query.answer()
    await callback_query.message.edit_caption(
        "🎵 ʜᴏᴡ ᴛᴏ ᴘʟᴀʏ ᴍᴜsɪᴄ:\n\n"
        "sᴇɴᴅ: /ᴘʟᴀʏ sᴏɴɢ ɴᴀᴍᴇ\n\n"
        "ᴇxᴀᴍᴘʟᴇ: /ᴘʟᴀʏ ɴᴇᴠᴇʀ ɢᴏɴɴᴀ ɢɪᴠᴇ ʏᴏᴜ ᴜᴘ\n\n"
        "ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ sᴇᴀʀᴄʜ ʏᴏᴜᴛᴜʙᴇ ᴀɴᴅ ᴀᴅᴅ ɪᴛ ᴛᴏ ᴛʜᴇ qᴜᴇᴜᴇ!",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("commands"))
async def commands_callback(client, callback_query):
    """Show all commands"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback_query.answer()
    await callback_query.message.edit_caption(
        "🎵 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs:\n\n"
        "• /sᴛᴀʀᴛ - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n"
        "• /ᴘʟᴀʏ [sᴏɴɢ] - ᴘʟᴀʏ ᴀ sᴏɴɢ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ\n"
        "• /qᴜᴇᴜᴇ - sʜᴏᴡ ᴄᴜʀʀᴇɴᴛ qᴜᴇᴜᴇ\n"
        "• /sᴛᴏᴘ - sᴛᴏᴘ ᴘʟᴀʏɪɴɢ\n"
        "• /ᴀʙᴏᴜᴛ - ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ\n"
        "• /ʜᴇʟᴘ - sʜᴏᴡ ʜᴇʟᴘ ᴍᴇssᴀɢᴇ",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("about"))
async def about_callback(client, callback_query):
    """Show about info"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton("📢 sᴜᴘᴘ", url="https://t.me/aethosupport")
        ],
        [InlineKeyboardButton("← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback_query.answer()
    await callback_query.message.edit_caption(
        "ℹ️ ᴀʙᴏᴜᴛ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ\n\n"
        "🎵 ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ʙᴏᴛ\n"
        "📱 ᴘʟᴀʏ ʏᴏᴜᴛᴜʙᴇ ᴍᴜsɪᴄ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs\n"
        "⚡ ғᴀsᴛ & ʀᴇʟɪᴀʙʟᴇ\n"
        "🔧 ʙᴜɪʟᴛ ᴡɪᴛʜ ᴘʏᴛʜᴏɴ & ᴘʏʀᴏɢʀᴀᴍ\n\n"
        "ᴅᴇᴠᴇʟᴏᴘᴇʀ: ᴇʀᴇɴ-ᴛᴇᴄʜ26\n"
        "ᴠᴇʀsɪᴏɴ: 1.0\n"
        "sᴛᴀᴛᴜs: ᴀᴄᴛɪᴠᴇ ✅",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("modules"))
async def modules_callback(client, callback_query):
    """Show modules"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback_query.answer()
    await callback_query.message.edit_caption(
        "🛠️ ᴀᴇᴛʜᴏ ᴍᴏᴅᴜʟᴇs\n\n"
        "✅ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ - ᴘʟᴀʏ ᴍᴜsɪᴄ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ\n"
        "✅ qᴜᴇᴜᴇ ᴍᴀɴᴀɢᴇʀ - ᴍᴀɴᴀɢᴇ ᴘʟᴀʏʟɪsᴛs\n"
        "🔄 ᴄᴏᴍɪɴɢ sᴏᴏɴ: sᴘᴏᴛɪғʏ sᴜᴘᴘᴏʀᴛ\n"
        "🔄 ᴄᴏᴍɪɴɢ sᴏᴏɴ: ᴘʟᴀʏʟɪsᴛ sᴀᴠᴇ\n"
        "🔄 ᴄᴏᴍɪɴɢ sᴏᴏɴ: ᴍᴜsɪᴄ ʟʏʀɪᴄs\n"
        "🔄 ᴄᴏᴍɪɴɢ sᴏᴏɴ: ᴀᴜᴅɪᴏ ᴇғғᴇᴄᴛs",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("back_start"))
async def back_start(client, callback_query):
    """Go back to start"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▶️ ᴘʟᴀʏ", callback_data="play_music"),
            InlineKeyboardButton("📝 ᴄᴏᴍᴍᴀɴᴅs", callback_data="commands")
        ],
        [
            InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton("🛠️ ᴍᴏᴅᴜʟᴇs", callback_data="modules")
        ],
        [
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/aethosupport")
        ],
        [
            InlineKeyboardButton("🔗 ɴᴇᴛᴡᴏʀᴋ", url="https://t.me/Aethonix_network")
        ]
    ])
    await callback_query.answer()
    await callback_query.message.edit_caption(
        "🎵 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ! 🎵\n\n"
        "ᴘʟᴀʏ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ sᴏɴɢs ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ɪɴ ᴛᴇʟᴇɢʀᴀᴍ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs!\n\n"
        "ᴜsᴇ /ᴘʟᴀʏ [sᴏɴɢ ɴᴀᴍᴇ] ᴛᴏ sᴛᴀʀᴛ ᴘʟᴀʏɪɴɢ ᴍᴜsɪᴄ.\n\n"
        "ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴇxᴘʟᴏʀᴇ!",
        reply_markup=keyboard
    )

@app.on_message(filters.command("play"))
async def play(client, message: Message):
    """Play a song from YouTube"""
    if len(message.command) < 2:
        await message.reply("❌ ᴜsᴀɢᴇ: `/ᴘʟᴀʏ [sᴏɴɢ ɴᴀᴍᴇ]`")
        return
    
    query = " ".join(message.command[1:])
    await message.reply(f"🔍 sᴇᴀʀᴄʜɪɴɢ ғᴏʀ: `{query}`...")
    
    song_info = search_youtube(query)
    if not song_info:
        await message.reply("❌ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ!")
        return
    
    song_title = song_info.get('title', 'Unknown')
    song_url = song_info.get('url', '')
    
    current_queue.append({
        'title': song_title,
        'url': song_url,
        'uploader': song_info.get('uploader', 'Unknown')
    })
    
    await message.reply(
        f"✅ ᴀᴅᴅᴇᴅ ᴛᴏ qᴜᴇᴜᴇ:\n"
        f"🎵 **{song_title}**\n"
        f"👤 ʙʏ: {song_info.get('uploader', 'Unknown')}"
    )

@app.on_message(filters.command("queue"))
async def queue_cmd(client, message: Message):
    """Show current queue"""
    if not current_queue:
        await message.reply("📭 qᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ!")
        return
    
    queue_text = "🎵 ᴄᴜʀʀᴇɴᴛ qᴜᴇᴜᴇ:\n\n"
    for i, song in enumerate(current_queue, 1):
        queue_text += f"{i}. {song['title']}\n"
    
    await message.reply(queue_text)

@app.on_message(filters.command("stop"))
async def stop(client, message: Message):
    """Stop music"""
    global is_playing
    is_playing = False
    current_queue.clear()
    await message.reply("⏹️ ᴍᴜsɪᴄ sᴛᴏᴘᴘᴇᴅ!")

@app.on_message(filters.command("about"))
async def about(client, message: Message):
    """Show about"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton("📢 sᴜᴘᴘ", url="https://t.me/aethosupport")
        ]
    ])
    await message.reply(
        "ℹ️ ᴀʙᴏᴜᴛ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ\n\n"
        "🎵 ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ʙᴏᴛ\n"
        "📱 ᴘʟᴀʏ ʏᴏᴜᴛᴜʙᴇ ᴍᴜsɪᴄ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs\n"
        "⚡ ғᴀsᴛ & ʀᴇʟɪᴀʙʟᴇ\n"
        "🔧 ʙᴜɪʟᴛ ᴡɪᴛʜ ᴘʏᴛʜᴏɴ & ᴘʏʀᴏɢʀᴀᴍ\n\n"
        "ᴅᴇᴠᴇʟᴏᴘᴇʀ: ᴇʀᴇɴ-ᴛᴇᴄʜ26\n"
        "ᴠᴇʀsɪᴏɴ: 1.0\n"
        "sᴛᴀᴛᴜs: ᴀᴄᴛɪᴠᴇ ✅",
        reply_markup=keyboard
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    """Show help"""
    await message.reply(
        "🎵 ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ - ʜᴇʟᴘ\n\n"
        "ᴄᴏᴍᴍᴀɴᴅs:\n"
        "• /sᴛᴀʀᴛ - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n"
        "• /ᴘʟᴀʏ [sᴏɴɢ] - ᴘʟᴀʏ ᴀ sᴏɴɢ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ\n"
        "• /qᴜᴇᴜᴇ - sʜᴏᴡ ᴄᴜʀʀᴇɴᴛ qᴜᴇᴜᴇ\n"
        "• /sᴛᴏᴘ - sᴛᴏᴘ ᴘʟᴀʏɪɴɢ\n"
        "• /ᴀʙᴏᴜᴛ - ʙᴏᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ\n"
        "• /ʜᴇʟᴘ - sʜᴏᴡ ᴛʜɪs ᴍᴇssᴀɢᴇ\n\n"
        "ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ ᴇʀᴇɴ-ᴛᴇᴄʜ26"
    )

if __name__ == "__main__":
    logger.info("🎵 Aetho Music Bot started!")
    app.run()
