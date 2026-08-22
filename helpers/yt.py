import yt_dlp
import os

YDL_OPTS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'socket_timeout': 30,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
    'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
}

async def download_song(video_id: str):
    """Download song from YouTube"""
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get("url"), info.get("title"), info.get("thumbnail")
    except Exception as e:
        print(f"Error: {e}")
    return None, None, None
