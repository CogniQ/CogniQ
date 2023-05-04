import aiohttp
from .config import Config


def map_search_type_to_path(search_type):
    search_type_to_path = {
        "web": "/v7.0/search",
        # "image": "/v7.0/images/search",
        # "video": "/v7.0/videos/search",
        "news": "/v7.0/news/search",
        # "spellcheck": "/v7.0/spellcheck",
        # "autosuggest": "/v7.0/suggestions",
        # "entity": "/v7.0/entities",
        # "relatedsearch": "/v7.0/entities",
        # "completesuggestions": "/v7.0/entities",
    }
    return search_type_to_path.get(search_type, "/v7.0/search")


async def async_bing_search(*, q, search_type="web", **kwargs):
    url = Config["BING_SEARCH_ENDPOINT"] + map_search_type_to_path(search_type)
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": Config["BING_SUBSCRIPTION_KEY"],
        "X-Search-Location": "lat:37.79003;long:-122.40074;re:100",  # https://github.com/CognIQ/CogniQ/issues/1
    }
    params = {"q": q, "mkt": "en-US", **kwargs}

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(
                    f"Error reaching {url} [{response.status}]: {await response.text()}"
                )