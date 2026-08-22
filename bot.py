import logging
from pyrogram import Client, filters
from pyrogram.types import Message
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
    """Start command"""
    await message.reply(
        "🎵 **Aetho Music Bot**\n\n"
        "Commands:\n"
        "• `/play [song name]` - Play a song\n"
        "• `/stop` - Stop music\n"
        "• `/queue` - Show queue\n"
        "• `/help` - Show this message"
    )

@app.on_message(filters.command("play"))
async def play(client, message: Message):
    """Play a song from YouTube"""
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/play [song name]`")
        return
    
    query = " ".join(message.command[1:])
    await message.reply(f"🔍 Searching for: `{query}`...")
    
    song_info = search_youtube(query)
    if not song_info:
        await message.reply("❌ Song not found!")
        return
    
    song_title = song_info.get('title', 'Unknown')
    song_url = song_info.get('url', '')
    
    current_queue.append({
        'title': song_title,
        'url': song_url,
        'uploader': song_info.get('uploader', 'Unknown')
    })
    
    await message.reply(
        f"✅ Added to queue:\n"
        f"🎵 **{song_title}**\n"
        f"👤 By: {song_info.get('uploader', 'Unknown')}"
    )

@app.on_message(filters.command("queue"))
async def queue_cmd(client, message: Message):
    """Show current queue"""
    if not current_queue:
        await message.reply("📭 Queue is empty!")
        return
    
    queue_text = "🎵 **Current Queue:**\n\n"
    for i, song in enumerate(current_queue, 1):
        queue_text += f"{i}. {song['title']}\n"
    
    await message.reply(queue_text)

@app.on_message(filters.command("stop"))
async def stop(client, message: Message):
    """Stop music"""
    global is_playing
    is_playing = False
    current_queue.clear()
    await message.reply("⏹️ Music stopped!")

@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    """Show help"""
    await message.reply(
        "🎵 **Aetho Music Bot - Help**\n\n"
        "Commands:\n"
        "• `/start` - Start the bot\n"
        "• `/play [song]` - Play a song from YouTube\n"
        "• `/queue` - Show current queue\n"
        "• `/stop` - Stop playing\n"
        "• `/help` - Show this message\n\n"
        "Made with ❤️ by Eren-tech26"
    )

if __name__ == "__main__":
    logger.info("🎵 Aetho Music Bot started!")
    app.run()
