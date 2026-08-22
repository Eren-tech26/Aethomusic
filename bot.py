import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
import yt_dlp
import aiohttp
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

current_queue = []

def search_youtube(query):
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info and 'entries' in info:
                return info['entries'][0]
    except Exception as e:
        logger.error(f"Error: {e}")
    return None

@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ ᴘʟᴀʏ", callback_data="play_music"),
            InlineKeyboardButton(text="📝 ᴄᴏᴍᴍᴀɴᴅs", callback_data="commands")
        ],
        [
            InlineKeyboardButton(text="ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton(text="🛠️ ᴍᴏᴅᴜʟᴇs", callback_data="modules")
        ],
        [
            InlineKeyboardButton(text="👨‍💻 ᴅᴇᴠ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton(text="📢 sᴜᴘᴘ", url="https://t.me/aethosupport")
        ],
        [
            InlineKeyboardButton(text="🔗 ɴᴇᴛᴡᴏʀᴋ", url="https://t.me/Aethonix_network")
        ]
    ])
    await message.reply_photo(
        photo="https://telegra.ph/file/your-image.jpg",
        caption="🎵 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ! 🎵\n\nᴜsᴇ /ᴘʟᴀʏ [sᴏɴɢ]",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "play_music")
async def play_callback(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]])
    await callback.message.edit_caption("🎵 ᴜsᴇ: /ᴘʟᴀʏ [sᴏɴɢ ɴᴀᴍᴇ]", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "commands")
async def commands_callback(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]])
    await callback.message.edit_caption("🎵 ᴄᴏᴍᴍᴀɴᴅs:\n/ᴘʟᴀʏ /qᴜᴇᴜᴇ /sᴛᴏᴘ /ʜᴇʟᴘ", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]])
    await callback.message.edit_caption("ℹ️ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ ʙʏ ᴇʀᴇɴ-ᴛᴇᴄʜ26", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "modules")
async def modules_callback(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]])
    await callback.message.edit_caption("🛠️ ᴍᴏᴅᴜʟᴇs:\n✅ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ\n🔄 ᴍᴏʀᴇ sᴏᴏɴ", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "back_start")
async def back_start(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ ᴘʟᴀʏ", callback_data="play_music"),
            InlineKeyboardButton(text="📝 ᴄᴏᴍᴍᴀɴᴅs", callback_data="commands")
        ],
        [
            InlineKeyboardButton(text="ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton(text="🛠️ ᴍᴏᴅᴜʟᴇs", callback_data="modules")
        ],
        [
            InlineKeyboardButton(text="👨‍💻 ᴅᴇᴠ", url="https://t.me/eren_aethonix"),
            InlineKeyboardButton(text="📢 sᴜᴘᴘ", url="https://t.me/aethosupport")
        ],
        [
            InlineKeyboardButton(text="🔗 ɴᴇᴛᴡᴏʀᴋ", url="https://t.me/Aethonix_network")
        ]
    ])
    await callback.message.edit_caption("🎵 ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ!", reply_markup=keyboard)
    await callback.answer()

@dp.message(Command("play"))
async def play(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ ᴜsᴀɢᴇ: /ᴘʟᴀʏ [sᴏɴɢ]")
        return
    query = args[1]
    status = await message.reply(f"🔍 sᴇᴀʀᴄʜɪɴɢ: {query}...")
    song = search_youtube(query)
    if not song:
        await status.edit_text("❌ ɴᴏᴛ ғᴏᴜɴᴅ!")
        return
    current_queue.append(song)
    audio_url = song.get('url')
    title = song.get('title', 'Unknown')
    await status.edit_text(f"⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ: {title}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url) as resp:
                data = await resp.read()
        await message.answer_audio(
            BufferedInputFile(data, filename=f"{title}.mp3"),
            title=title
        )
        await status.delete()
    except Exception as e:
        logger.error(f"Download error: {e}")
        await status.edit_text("❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴛʀᴇᴀᴍ. ᴛʀʏ ᴀɴᴏᴛʜᴇʀ sᴏɴɢ.")

@dp.message(Command("queue"))
async def queue_cmd(message: types.Message):
    if not current_queue:
        await message.reply("📭 ᴇᴍᴘᴛʏ!")
        return
    text = "🎵 qᴜᴇᴜᴇ:\n\n" + "\n".join(f"{i}. {s.get('title')}" for i, s in enumerate(current_queue, 1))
    await message.reply(text)

@dp.message(Command("stop"))
async def stop(message: types.Message):
    current_queue.clear()
    await message.reply("⏹️ sᴛᴏᴘᴘᴇᴅ!")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.reply("🎵 /ᴘʟᴀʏ /qᴜᴇᴜᴇ /sᴛᴏᴘ")

async def handle_ping(request):
    return web.Response(text="Bot is alive")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server running on port {port}")

async def main():
    logger.info("🎵 Bot started!")
    await bot.delete_webhook(drop_pending_updates=True)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
