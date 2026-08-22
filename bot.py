import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
from config import BOT_TOKEN

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Store queue
current_queue = []

def search_youtube(query):
    """Search YouTube for a song"""
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
    """Start command"""
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
        photo="https://ibb.co/9mKvy2dM",
        caption="🎵 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ! 🎵\n\nᴘʟᴀʏ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ sᴏɴɢs ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ!\n\nᴜsᴇ /ᴘʟᴀʏ [sᴏɴɢ]",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "play_music")
async def play_callback(callback: types.CallbackQuery):
    """Play button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback.message.edit_caption(
        "🎵 ᴜsᴇ: /ᴘʟᴀʏ [sᴏɴɢ ɴᴀᴍᴇ]\n\nᴇxᴀᴍᴘʟᴇ: /ᴘʟᴀʏ ɴᴇᴠᴇʀ ɢᴏɴɴᴀ ɢɪᴠᴇ ʏᴏᴜ ᴜᴘ",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "commands")
async def commands_callback(callback: types.CallbackQuery):
    """Commands button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback.message.edit_caption(
        "🎵 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs:\n\n"
        "• /ᴘʟᴀʏ [sᴏɴɢ] - ᴘʟᴀʏ ᴍᴜsɪᴄ\n"
        "• /qᴜᴇᴜᴇ - sʜᴏᴡ qᴜᴇᴜᴇ\n"
        "• /sᴛᴏᴘ - sᴛᴏᴘ ᴘʟᴀʏɪɴɢ\n"
        "• /ʜᴇʟᴘ - sʜᴏᴡ ʜᴇʟᴘ",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_callback(callback: types.CallbackQuery):
    """About button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback.message.edit_caption(
        "ℹ️ ᴀʙᴏᴜᴛ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ\n\n"
        "🎵 ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ʙᴏᴛ\n"
        "ᴅᴇᴠᴇʟᴏᴘᴇʀ: ᴇʀᴇɴ-ᴛᴇᴄʜ26\n"
        "ᴠᴇʀsɪᴏɴ: 1.0 ✅",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "modules")
async def modules_callback(callback: types.CallbackQuery):
    """Modules button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← ʙᴀᴄᴋ", callback_data="back_start")]
    ])
    await callback.message.edit_caption(
        "🛠️ ᴀᴇᴛʜᴏ ᴍᴏᴅᴜʟᴇs\n\n"
        "✅ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ\n"
        "✅ qᴜᴇᴜᴇ ᴍᴀɴᴀɢᴇʀ\n"
        "🔄 ᴄᴏᴍɪɴɢ sᴏᴏɴ: sᴘᴏᴛɪғʏ",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "back_start")
async def back_start(callback: types.CallbackQuery):
    """Back to start"""
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
    await callback.message.edit_caption(
        "🎵 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ! 🎵",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.message(Command("play"))
async def play(message: types.Message):
    """Play command"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ ᴜsᴀɢᴇ: /ᴘʟᴀʏ [sᴏɴɢ]")
        return
    
    query = args[1]
    await message.reply(f"🔍 sᴇᴀʀᴄʜɪɴɢ: {query}...")
    
    song = search_youtube(query)
    if not song:
        await message.reply("❌ ɴᴏᴛ ғᴏᴜɴᴅ!")
        return
    
    current_queue.append(song)
    await message.reply(f"✅ ᴀᴅᴅᴇᴅ: {song.get('title')}")

@dp.message(Command("queue"))
async def queue_cmd(message: types.Message):
    """Show queue"""
    if not current_queue:
        await message.reply("📭 ᴇᴍᴘᴛʏ!")
        return
    
    text = "🎵 qᴜᴇᴜᴇ:\n\n"
    for i, song in enumerate(current_queue, 1):
        text += f"{i}. {song.get('title')}\n"
    await message.reply(text)

@dp.message(Command("stop"))
async def stop(message: types.Message):
    """Stop command"""
    current_queue.clear()
    await message.reply("⏹️ sᴛᴏᴘᴘᴇᴅ!")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    """Help command"""
    await message.reply(
        "🎵 ᴀᴇᴛʜᴏ ᴍᴜsɪᴄ ʙᴏᴛ\n\n"
        "ᴄᴏᴍᴍᴀɴᴅs:\n"
        "• /ᴘʟᴀʏ - ᴘʟᴀʏ ᴍᴜsɪᴄ\n"
        "• /qᴜᴇᴜᴇ - sʜᴏᴡ qᴜᴇᴜᴇ\n"
        "• /sᴛᴏᴘ - sᴛᴏᴘ"
    )

async def main():
    """Main function"""
    logger.info("🎵 Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
