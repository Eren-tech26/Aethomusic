import asyncio
import logging
import os
import io
import aiohttp
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from config import BOT_TOKEN, API_ID, API_HASH, SESSION_STRING

import time as _time
START_TIME = _time.time()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = Client("aethomusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("aethomusic_assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(assistant)

queues = {}
active_calls = set()
loop_enabled = set()

INVIDIOUS_INSTANCES = [ # updated
    "https://invidious.kavin.rocks",
    "https://vid.puffyan.us",
    "https://y.com.sb",
    "https://invidious.nerdvpn.de",
    "https://invidious.snopyta.org",
]

async def invidious_search(query):
    async with aiohttp.ClientSession() as session:
        for instance in INVIDIOUS_INSTANCES:
            try:
                url = f"{instance}/api/v1/search?q={aiohttp.helpers.quote(query)}&type=video&fields=videoId,title,videoThumbnails"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            return data[0], instance
            except Exception as e:
                logger.warning(f"Invidious search failed on {instance}: {e}")
                continue
    return None, None

async def invidious_stream_url(video_id, instance):
    async with aiohttp.ClientSession() as session:
        for inst in [instance] + [i for i in INVIDIOUS_INSTANCES if i != instance]:
            try:
                url = f"{inst}/api/v1/videos/{video_id}?fields=adaptiveFormats,title"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        formats = data.get("adaptiveFormats", [])
                        audio_formats = [f for f in formats if f.get("type", "").startswith("audio")]
                        if audio_formats:
                            best = sorted(audio_formats, key=lambda x: int(x.get("bitrate", 0)), reverse=True)[0]
                            return best.get("url")
            except Exception as e:
                logger.warning(f"Invidious stream failed on {inst}: {e}")
                continue
    return None

def get_uptime():
    seconds = int(_time.time() - START_TIME)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days}ᴅ {hours}ʜ {minutes}ᴍ {seconds}s"

async def get_edited_thumbnail(thumb_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumb_url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                data = await resp.read()
                img = Image.open(io.BytesIO(data)).convert("RGB")
                img = img.resize((640, 360))
                img = img.filter(ImageFilter.GaussianBlur(radius=10))
                draw = ImageDraw.Draw(img)
                text = "ᴀᴇᴛʜᴏɴɪx ᴍᴜsɪᴄ"
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                except Exception:
                    font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), text, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                x, y = (640 - w) / 2, (360 - h) / 2
                draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 180))
                draw.text((x, y), text, font=font, fill=(255, 255, 255))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=90)
                buf.seek(0)
                buf.name = "thumb.jpg"
                return buf
    except Exception as e:
        logger.error(f"Thumbnail error: {e}")
        return None

def build_controls(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏮ ᴘʀᴇᴠ", callback_data=f"prev_{chat_id}"),
            InlineKeyboardButton("⏯ ᴘᴀᴜsᴇ", callback_data=f"pause_resume_{chat_id}"),
            InlineKeyboardButton("⏭ ɴᴇxᴛ", callback_data=f"skip_{chat_id}"),
        ],
        [
            InlineKeyboardButton("🔁 ʟᴏᴏᴘ", callback_data=f"loop_{chat_id}"),
            InlineKeyboardButton("📜 ǫᴜᴇᴜᴇ", callback_data=f"queue_{chat_id}"),
            InlineKeyboardButton("⏹ sᴛᴏᴘ", callback_data=f"stop_{chat_id}"),
        ],
    ])

@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
        [InlineKeyboardButton("❓ ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="commands")],
        [
            InlineKeyboardButton("👨‍💻 ᴏᴡɴᴇʀ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/aethosupport"),
        ],
        [InlineKeyboardButton("🔗 ᴄʜᴀɴɴᴇʟ", url="https://t.me/Aethonix_network")],
    ])
    caption = (
        "──── 「 ᴀᴇᴛʜᴏɴɪx ᴍᴜsɪᴄ 」 ────\n\n"
        f"ʜᴏʟᴀ 耀•|{message.from_user.first_name}!!\n\n"
        "ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴍᴜsɪᴄ ʙᴏᴛ.\n"
        "- - - - - - - - - - - -\n"
        f"➥ ᴜᴘᴛɪᴍᴇ: {get_uptime()}\n"
        "➥ sᴇʀᴠᴇʀ: ʀᴇɴᴅᴇʀ ᴄʟᴏᴜᴅ\n"
        "- - - - - - - - - - - -\n\n"
        "ᴜsᴇ /ʜᴇʟᴘ ᴛᴏ sᴇᴇ ᴄᴏᴍᴍᴀɴᴅs."
    )
    await message.reply_photo(
        photo="https://i.ibb.co/9mKvy2dM/196647.png",
        caption=caption,
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

    s1 = await message.reply("🪄")
    await asyncio.sleep(0.8)
    await s1.edit("🔍 sᴇᴀʀᴄʜɪɴɢ...")
    await asyncio.sleep(0.8)
    await s1.edit("⬇️ ғᴇᴛᴄʜɪɴɢ ᴀᴜᴅɪᴏ...")
    await asyncio.sleep(0.5)
    await s1.edit("🎧 ᴘʀᴇᴘᴀʀɪɴɢ sᴛʀᴇᴀᴍ...")

    result, instance = await invidious_search(query)

    if not result:
        await s1.edit("❌ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ!")
        return

    video_id = result.get("videoId")
    title = result.get("title", "Unknown")
    thumbs = result.get("videoThumbnails", [])
    thumb_url = thumbs[0].get("url") if thumbs else None

    stream_url = await invidious_stream_url(video_id, instance)

    if not stream_url:
        await s1.edit("❌ sᴛʀᴇᴀᴍ ᴜʀʟ ɴᴏᴛ ғᴏᴜɴᴅ!")
        return

    await s1.delete()

    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append({"url": stream_url, "title": title, "thumb": thumb_url})

    if chat_id in active_calls:
        await message.reply(f"📝 ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ: {title}")
        return

    try:
        await call_py.play(chat_id, MediaStream(stream_url))
        active_calls.add(chat_id)
        thumb_buf = await get_edited_thumbnail(thumb_url) if thumb_url else None
        caption = f"🎵 ɴᴏᴡ ᴘʟᴀʏɪɴɢ\n\n**{title}**"
        if thumb_buf:
            await message.reply_photo(photo=thumb_buf, caption=caption, reply_markup=build_controls(chat_id))
        else:
            await message.reply(caption, reply_markup=build_controls(chat_id))
    except Exception as e:
        logger.error(f"Play error: {e}")
        await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")

@app.on_callback_query(filters.regex(r"^pause_resume_"))
async def cb_pause_resume(client, callback):
    chat_id = int(callback.data.split("_")[-1])
    try:
        await call_py.pause(chat_id)
        await callback.answer("⏸ ᴘᴀᴜsᴇᴅ")
    except Exception:
        try:
            await call_py.resume(chat_id)
            await callback.answer("▶️ ʀᴇsᴜᴍᴇᴅ")
        except Exception as e:
            await callback.answer(f"❌ {e}", show_alert=True)

@app.on_callback_query(filters.regex(r"^skip_"))
async def cb_skip(client, callback):
    chat_id = int(callback.data.split("_")[-1])
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

@app.on_callback_query(filters.regex(r"^prev_"))
async def cb_prev(client, callback):
    chat_id = int(callback.data.split("_")[-1])
    await callback.answer("⚠️ ɴᴏ ᴘʀᴇᴠɪᴏᴜs sᴏɴɢ", show_alert=True)

@app.on_callback_query(filters.regex(r"^loop_"))
async def cb_loop(client, callback):
    chat_id = int(callback.data.split("_")[-1])
    if chat_id in loop_enabled:
        loop_enabled.discard(chat_id)
        await callback.answer("🔁 ʟᴏᴏᴘ ᴏғғ")
    else:
        loop_enabled.add(chat_id)
        await callback.answer("🔁 ʟᴏᴏᴘ ᴏɴ")

@app.on_callback_query(filters.regex(r"^stop_"))
async def cb_stop(client, callback):
    chat_id = int(callback.data.split("_")[-1])
    queues.pop(chat_id, None)
    loop_enabled.discard(chat_id)
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass
    active_calls.discard(chat_id)
    await callback.answer("⏹ sᴛᴏᴘᴘᴇᴅ")

@app.on_callback_query(filters.regex(r"^queue_"))
async def cb_queue(client, callback):
    chat_id = int(callback.data.split("_")[-1])
    q = queues.get(chat_id, [])
    if not q:
        await callback.answer("📭 ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ", show_alert=True)
        return
    text = "\n".join(f"{i}. {s['title']}" for i, s in enumerate(q, 1))
    await callback.answer(text[:200], show_alert=True)

@app.on_message(filters.command("skip") & filters.group)
async def skip(client, message):
    chat_id = message.chat.id
    if chat_id in queues and queues[chat_id]:
        queues[chat_id].pop(0)
    if chat_id in queues and queues[chat_id]:
        next_song = queues[chat_id][0]
        await call_py.play(chat_id, MediaStream(next_song["url"]))
        await message.reply(f"⏭ sᴋɪᴘᴘᴇᴅ! ɴᴏᴡ ᴘʟᴀʏɪɴɢ: {next_song['title']}")
    else:
        await call_py.leave_call(chat_id)
        active_calls.discard(chat_id)
        await message.reply("⏹ ǫᴜᴇᴜᴇ ᴇɴᴅᴇᴅ!")

@app.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    chat_id = message.chat.id
    queues.pop(chat_id, None)
    loop_enabled.discard(chat_id)
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass
    active_calls.discard(chat_id)
    await message.reply("⏹ sᴛᴏᴘᴘᴇᴅ!")

@app.on_message(filters.command("pause") & filters.group)
async def pause(client, message):
    chat_id = message.chat.id
    try:
        await call_py.pause(chat_id)
        await message.reply("⏸ ᴘᴀᴜsᴇᴅ!")
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
        await message.reply("📭 ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ!")
        return
    text = "🎵 ǫᴜᴇᴜᴇ:\n\n" + "\n".join(f"{i}. {s['title']}" for i, s in enumerate(q, 1))
    await message.reply(text)

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply(
        "🎵 **ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ᴄᴏᴍᴍᴀɴᴅs**\n\n"
        "/play [song] — ᴘʟᴀʏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ\n"
        "/skip — sᴋɪᴘ ᴄᴜʀʀᴇɴᴛ\n"
        "/pause — ᴘᴀᴜsᴇ\n"
        "/resume — ʀᴇsᴜᴍᴇ\n"
        "/queue — sʜᴏᴡ ǫᴜᴇᴜᴇ\n"
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
    await assistant.start()
    await call_py.start()
    await start_web()
    logger.info("🎵 Bot live!")
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    loop.run_until_complete(main())
