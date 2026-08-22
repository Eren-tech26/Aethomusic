import asyncio
import logging
import os
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import yt_dlp
from config import BOT_TOKEN, API_ID, API_HASH

loop = asyncio.get_event_loop()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = Client("aethomusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

queues = {}
active_calls = set()

def get_audio_url(query):
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info and 'entries' in info:
                entry = info['entries'][0]
                return entry.get('url'), entry.get('title')
    except Exception as e:
        logger.error(f"yt_dlp error: {e}")
    return None, None

@app.on_message(filters.command("start"))
async def start(client, message):
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
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton("📢 sᴜᴘᴘ", url="https://t.me/aethosupport")
        ],
        [
            InlineKeyboardButton("🔗 ɴᴇᴛᴡᴏʀᴋ", url="https://t.me/Aethonix_network")
        ]
    ])
    await message.reply(
        "🎵 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ!\n\nᴜsᴇ /play [song] ɪɴ ᴀ ɢʀᴏᴜᴘ",
        reply_markup=keyboard
    )

@app.on_message(filters.command("play") & filters.group)
async def play(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ ᴜsᴀɢᴇ: /play [song name]")
        return

    chat_id = message.chat.id
    query = args[1]
    status = await message.reply(f"🔍 sᴇᴀʀᴄʜɪɴɢ: {query}...")

    url, title = get_audio_url(query)
    if not url:
        await status.edit("❌ ɴᴏᴛ ғᴏᴜɴᴅ!")
        return

    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append({"url": url, "title": title})

    if chat_id in active_calls:
        await status.edit(f"📝 ᴀᴅᴅᴇᴅ ᴛᴏ qᴜᴇᴜᴇ: {title}")
        return

    try:
        await call_py.play(chat_id, MediaStream(url))
        active_calls.add(chat_id)
        await status.edit(f"🎵 ᴘʟᴀʏɪɴɢ: {title}")
    except Exception as e:
        logger.error(f"Play error: {e}")
        await status.edit(f"❌ ᴇʀʀᴏʀ: {e}")

@app.on_message(filters.command("skip") & filters.group)
async def skip(client, message):
    chat_id = message.chat.id
    if chat_id in queues and queues[chat_id]:
        queues[chat_id].pop(0)
    if chat_id in queues and queues[chat_id]:
        next_song = queues[chat_id][0]
        await call_py.play(chat_id, MediaStream(next_song['url']))
        await message.reply(f"⏭️ sᴋɪᴘᴘᴇᴅ! ᴘʟᴀʏɪɴɢ: {next_song['title']}")
    else:
        await call_py.leave_call(chat_id)
        active_calls.discard(chat_id)
        await message.reply("⏹️ qᴜᴇᴜᴇ ᴇɴᴅᴇᴅ!")

@app.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    chat_id = message.chat.id
    queues.pop(chat_id, None)
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass
    active_calls.discard(chat_id)
    await message.reply("⏹️ sᴛᴏᴘᴘᴇᴅ!")

@app.on_message(filters.command("pause") & filters.group)
async def pause(client, message):
    chat_id = message.chat.id
    try:
        await call_py.pause(chat_id)
        await message.reply("⏸️ ᴘᴀᴜsᴇᴅ!")
    except Exception as e:
        await message.reply(f"❌ {e}")

@app.on_message(filters.command("resume") & filters.group)
async def resume(client, message):
    chat_id = message.chat.id
    try:
        await call_py.resume(chat_id)
        await message.reply("▶️ ʀᴇsᴜᴍᴇᴅ!")
    except Exception as e:
        await message.reply(f"❌ {e}")

@app.on_message(filters.command("queue") & filters.group)
async def queue_cmd(client, message):
    chat_id = message.chat.id
    q = queues.get(chat_id, [])
    if not q:
        await message.reply("📭 qᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ!")
        return
    text = "🎵 qᴜᴇᴜᴇ:\n\n" + "\n".join(f"{i}. {s['title']}" for i, s in enumerate(q, 1))
    await message.reply(text)

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply(
        "🎵 **ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ᴄᴏᴍᴍᴀɴᴅs**\n\n"
        "/play [song] — ᴘʟᴀʏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ\n"
        "/skip — sᴋɪᴘ ᴄᴜʀʀᴇɴᴛ\n"
        "/pause — ᴘᴀᴜsᴇ\n"
        "/resume — ʀᴇsᴜᴍᴇ\n"
        "/queue — sʜᴏᴡ qᴜᴇᴜᴇ\n"
        "/stop — sᴛᴏᴘ & ʟᴇᴀᴠᴇ"
    )

async def handle_ping(request):
    return web.Response(text="AethoMusic alive")

async def start_web():
    web_app = web.Application()
    web_app.router.add_get("/", handle_ping)
    runner = web.AppRunner(web_app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server on port {port}")

async def main():
    logger.info("🎵 AethoMusic starting...")
    await app.start()
    await call_py.start()
    await start_web()
    logger.info("🎵 Bot live!")
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    loop.run_until_complete(main())
