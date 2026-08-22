import aiohttp

async def download_song(query: str):
    try:
        async with aiohttp.ClientSession() as session:
            # Search for the video
            async with session.get(
                f"https://pipedapi.kavin.rocks/search?q={query}&filter=videos",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return None, None, None
                data = await resp.json()
                
            if not data.get("items"):
                return None, None, None
            
            video = data["items"][0]
            video_id = video["url"].split("=")[-1]
            title = video.get("title", query)
            thumbnail = video.get("thumbnail", "")
            
            # Get stream URL
            async with session.get(
                f"https://pipedapi.kavin.rocks/streams/{video_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as s:
                if s.status != 200:
                    return None, None, None
                stream_data = await s.json()
                
            if stream_data.get("audioStreams"):
                audio_url = stream_data["audioStreams"][0]["url"]
                return audio_url, title, thumbnail
                
    except Exception as e:
        print(f"Piped API Error: {e}")
    
    return None, None, None
