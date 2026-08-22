import aiohttp

async def download_song(query: str):
    """Use SafoneAPI - no bot detection"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.safone.me/search?query={query}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("results"):
                        result = data["results"][0]
                        return result.get("url"), result.get("title"), result.get("thumbnail")
    except Exception as e:
        print(f"API Error: {e}")
    return None, None, None
