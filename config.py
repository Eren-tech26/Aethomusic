import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Config
API_ID = int(os.getenv("API_ID", "21968859"))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
BOT_ID = int(BOT_TOKEN.split(":")[0])
BOT_USERNAME = os.getenv("BOT_USERNAME", "@aethomusic")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@eren_aethonix")
OWNER_ID = int(os.getenv("OWNER_ID", "7774827065"))

# Session string for assistant account
SESSION_STRING = os.getenv("SESSION_STRING", "")

# Music API (external - avoids YouTube bot detection)
API_URL = os.getenv("API_URL", "https://api.thequickearn.xyz")
VIDEO_API_URL = os.getenv("VIDEO_API_URL", "https://api.video.thequickearn.xyz")
API_KEY = os.getenv("API_KEY", "30DxNexGenBots107029")

# Spotify (optional)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

# Render/Heroku config
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", "aethomusic-bot")
PORT = int(os.getenv("PORT", 10000))

# Logging
LOGGER_ID = int(os.getenv("LOGGER_ID", "-1002812568647"))

# Bot settings
AUTO_LEAVING_ASSISTANT = os.getenv("AUTO_LEAVING_ASSISTANT", "False").lower() == "true"
AUTO_LEAVE_ASSISTANT_TIME = int(os.getenv("AUTO_LEAVE_ASSISTANT_TIME", "9000"))

# Limits
DURATION_LIMIT_MIN = int(os.getenv("DURATION_LIMIT_MIN", "500000"))
SONG_DOWNLOAD_DURATION = int(os.getenv("SONG_DOWNLOAD_DURATION", "9999999"))

# Images
START_IMG_URL = os.getenv("START_IMG_URL", "https://i.ibb.co/9mKvy2dM/196647.png")
PLAYLIST_IMG_URL = os.getenv("PLAYLIST_IMG_URL", START_IMG_URL)
YOUTUBE_IMG_URL = os.getenv("YOUTUBE_IMG_URL", START_IMG_URL)

# Bot name
BOT_NAME = os.getenv("BOT_NAME", "ᴀᴇᴛʜᴏɴɪx ᴍᴜsɪᴄ")
