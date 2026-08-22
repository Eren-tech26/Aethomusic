import asyncio
import logging
import os
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from helpers.yt import download_song as fetch_yt
from helpers.spotify import SpotifyAPI
from helpers.soundcloud import SoundCloudAPI
import time as _time

START_TIME = _time.time()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, PORT

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = Client("aethomusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("aethomusic_assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(assistant)

queues = {}
active_calls = set()
loop_enabled = set()

def get_uptime():
    seconds = int(_time.time() - START_TIME)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days}ᴅ {hours}ʜ {minutes}ᴍ {seconds}s"

async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except:
        return False

async def fetch_audio(query):
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            async with session.get(url) as resp:
                html = await resp.text()
                import re
                match = re.search(r'\"videoId\":\"([a-zA-Z0-9_-]{11})', html)
                if match:
                    vid_id = match.group(1)
                    return f"https://www.youtube.com/watch?v={vid_id}", query, f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg"
    except Exception as e:
        logger.error(f"Search error: {e}")
    return None, None, None

def build_controls(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ ᴘᴀᴜsᴇ", callback_data=f"pause_{chat_id}"),
            InlineKeyboardButton("⏭ sᴋɪᴘ", callback_data=f"skip_{chat_id}"),
            InlineKeyboardButton("⏹ sᴛᴏᴘ", callback_data=f"stop_{chat_id}"),
        ],
        [
            InlineKeyboardButton("🔁 ʟᴏᴏᴘ", callback_data=f"loop_{chat_id}"),
            InlineKeyboardButton("📜 ǫᴜᴇᴜᴇ", callback_data=f"queue_{chat_id}"),
        ]
    ])

@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
        [InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="commands")],
        [
            InlineKeyboardButton("👨‍💻 ᴏᴡɴᴇʀ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/aethosupport"),
        ],
    ])
    caption = (
        "──── 「 ᴀᴇᴛʜᴏɴɪx ᴍᴜsɪᴄ 」 ────\n\n"
        f"ʜᴏʟᴀ {message.from_user.first_name}!!\n\n"
        "ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴍᴜsɪᴄ ʙᴏᴛ.\n"
        "- - - - - - - - - - - -\n"
        f"➥ ᴜᴘᴛɪᴍᴇ: {get_uptime()}\n"
        "➥ sᴇʀᴠᴇʀ: ʀᴇɴᴅᴇʀ ᴄʟᴏᴜᴅ\n"
        "- - - - - - - - - - - -\n\n"
        "ᴜsᴇ /ʜᴇʟᴘ ᴛᴏ sᴇᴇ ᴄᴏᴍᴍᴀɴᴅs."
    )
    await message.reply_text(caption, reply_markup=keyboard)

@app.on_message(filters.command("play") & filters.group)
async def play(client, message):

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("❌ ᴜsᴀɢᴇ: /play [song name]")
    
    chat_id = message.chat.id
    query = args[1]
    
    s = await message.reply("🔍 sᴇᴀʀᴄʜɪɴɢ...")
    url, title, thumb = await fetch_audio(query)
    
    if not url:
        return await s.edit("❌ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ!")
    
    await s.delete()
    
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append({"url": url, "title": title, "thumb": thumb})
    
    if chat_id in active_calls:
        return await message.reply(f"📝 ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ: {title}")
    
    try:
        await call_py.play(chat_id, MediaStream(url))
        active_calls.add(chat_id)
        await message.reply(f"🎵 ɴᴏᴡ ᴘʟᴀʏɪɴɢ: **{title}**", reply_markup=build_controls(chat_id))
    except Exception as e:
        logger.error(f"Play error: {e}")
        await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")

@app.on_callback_query(filters.regex(r"^pause_"))
async def pause_resume(client, callback):
    chat_id = int(callback.data.split("_")[1])
    if not await is_admin(chat_id, callback.from_user.id):
        return await callback.answer("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ", show_alert=True)
    
    try:
        await call_py.pause(chat_id)
        await callback.answer("⏸ ᴘᴀᴜsᴇᴅ")
    except:
        try:
            await call_py.resume(chat_id)
            await callback.answer("▶️ ʀᴇsᴜᴍᴇᴅ")
        except Exception as e:
            await callback.answer(f"❌ {e}", show_alert=True)

@app.on_callback_query(filters.regex(r"^skip_"))
async def skip(client, callback):
    chat_id = int(callback.data.split("_")[1])
    if not await is_admin(chat_id, callback.from_user.id):
        return await callback.answer("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ", show_alert=True)
    
    if chat_id in queues and queues[chat_id]:
        queues[chat_id].pop(0)
    if chat_id in queues and queues[chat_id]:
        next_song = queues[chat_id][0]
        await call_py.play(chat_id, MediaStream(next_song["url"]))
        await callback.answer(f"⏭ {next_song['title'][:30]}")
    else:
        await call_py.leave_call(chat_id)
        active_calls.discard(chat_id)
        await callback.answer("⏹ ǫᴜᴇᴜᴇ ᴇɴᴅᴇᴅ")

@app.on_callback_query(filters.regex(r"^loop_"))
async def loop_toggle(client, callback):
    chat_id = int(callback.data.split("_")[1])
    if not await is_admin(chat_id, callback.from_user.id):
        return await callback.answer("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ", show_alert=True)
    
    if chat_id in loop_enabled:
        loop_enabled.discard(chat_id)
        await callback.answer("🔁 ʟᴏᴏᴘ ᴏғғ")
    else:
        loop_enabled.add(chat_id)
        await callback.answer("🔁 ʟᴏᴏᴘ ᴏɴ")

@app.on_callback_query(filters.regex(r"^stop_"))
async def stop(client, callback):
    chat_id = int(callback.data.split("_")[1])
    if not await is_admin(chat_id, callback.from_user.id):
        return await callback.answer("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ", show_alert=True)
    
    queues.pop(chat_id, None)
    loop_enabled.discard(chat_id)
    try:
        await call_py.leave_call(chat_id)
    except:
        pass
    active_calls.discard(chat_id)
    await callback.answer("⏹ sᴛᴏᴘᴘᴇᴅ")

@app.on_callback_query(filters.regex(r"^queue_"))
async def show_queue(client, callback):
    chat_id = int(callback.data.split("_")[1])
    q = queues.get(chat_id, [])
    if not q:
        return await callback.answer("📭 ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ", show_alert=True)
    text = "🎵 **ǫᴜᴇᴜᴇ:**\n\n"
    for i, s in enumerate(q, 1):
        text += f"{i}. {s['title'][:50]}\n"
    await callback.answer(text[:200], show_alert=True)

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    help_text = (
        "🎵 **ᴀᴇᴛʜᴏɴɪx ᴍᴜsɪᴄ ᴄᴏᴍᴍᴀɴᴅs**\n\n"
        "/play [song] — ᴘʟᴀʏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ\n"
        "/skip — sᴋɪᴘ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ\n"
        "/stop — sᴛᴏᴘ & ʟᴇᴀᴠᴇ ᴠᴄ\n"
        "/help — sʜᴏᴡ ᴛʜɪs ᴍᴇssᴀɢᴇ\n\n"
        "⚙️ **ᴀᴅᴍɪɴs ᴏɴʟʏ** - ᴘʟᴀʏ, sᴋɪᴘ, sᴛᴏᴘ"
    )
    await message.reply_text(help_text)

async def health_check(request):
    return web.Response(text="AethoMusic alive")

async def start_web():
    app_web = web.Application()
    app_web.router.add_get("/", health_check)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Web server on port {PORT}")

async def main():
    logger.info("🎵 AethoMusic starting...")
    await app.start()
    await assistant.start()
    await call_py.start()
    await start_web()
    logger.info("🎵 Bot live!")
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    loop.run_until_complete(main())
