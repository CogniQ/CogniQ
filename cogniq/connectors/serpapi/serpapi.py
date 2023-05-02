from serpapi import GoogleSearch

import aiohttp

from .config import Config


async def asynch_google_search_engine_results(*, q, **kwargs):
    url = f"https://serpapi.com/search"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "q": q,
        "api_key": Config["SERPAPI_API_KEY"],
        "engine": "google",
        "gl": "us",
        "hl": "en",
        "output": "json",
        **kwargs,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Error {response.status}: {await response.text()}")
