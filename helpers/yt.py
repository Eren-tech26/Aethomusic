import yt_dlp
import asyncio

YDL_OPTS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'socket_timeout': 30,
    'cookiefile': 'cookies.txt',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
}

async def download_song(query: str):
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = await loop.run_in_executor(None,
                lambda: ydl.extract_info(f"ytsearch:{query}", download=False)
            )
            if info and "entries" in info and info["entries"]:
                entry = info["entries"][0]
                return entry.get("url"), entry.get("title"), entry.get("thumbnail")
    except Exception as e:
        print(f"Error: {e}")
    return None, None, None
