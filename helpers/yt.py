import yt_dlp
import os

YDL_OPTS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'socket_timeout': 30,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
    'cookiefile': 'cookies.txt',
}

async def download_song(query: str):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info and "entries" in info and info["entries"]:
                entry = info["entries"][0]
                return entry.get("url"), entry.get("title"), entry.get("thumbnail")
    except Exception as e:
        print(f"Error: {e}")
    return None, None, None
