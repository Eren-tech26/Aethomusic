import aiohttp
import asyncio

async def download_song(query: str):
    """Fetch from external API instead of YouTube directly"""
    try:
        async with aiohttp.ClientSession() as session:
            # Use thequickearn API
            async with session.get(
                f"https://api.thequickearn.xyz/search?q={query}&type=audio",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("results"):
                        result = data["results"][0]
                        return result.get("url"), result.get("title"), result.get("thumbnail")
    except Exception as e:
        print(f"API Error: {e}")
    
    # Fallback: return YouTube search link
    return f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}", query, None
