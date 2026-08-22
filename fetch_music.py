import aiohttp
from config import API_URL, API_KEY

async def fetch_audio_via_api(query):
    """Fetch audio from external API instead of yt-dlp"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/search",
                params={"q": query, "type": "audio"},
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("results"):
                        result = data["results"][0]
                        return result.get("url"), result.get("title"), result.get("thumbnail")
    except Exception as e:
        print(f"API error: {e}")
    return None, None, None
