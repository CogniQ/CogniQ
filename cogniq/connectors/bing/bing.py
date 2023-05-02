from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .config import Config

import aiohttp
from cogniq.models.openai.best_search_result import get_best_search_result
from cogniq.connectors.bing.search_results import parse_search_results


def map_searchtype_to_path(searchtype):
    searchtype_to_path = {
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
    return searchtype_to_path.get(searchtype, "/v7.0/search")


async def async_bing_search(*, q, searchtype, **kwargs):
    url = Config["BING_SEARCH_ENDPOINT"] + map_searchtype_to_path(searchtype)
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": {Config["BING_SUBSCRIPTION_KEY"]},
        "X-Search-Location": "lat:37.79003;long:-122.40074;re:100",  # https://github.com/CognIQ/CogniQ/issues/1
    }
    payload = {"q": q, "mkt": "en-US", **kwargs}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            Config["BING_SEARCH_URL"], json=payload, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Error {response.status}: {await response.text()}")


def search_prompt(*, search_results, q):
    return f"""
    {search_results}

    {q}
    """


async def search(*, q, original_q):
    search_results = await async_bing_search(q, num_results=4)
    # best_search_result = await get_best_search_result(q=original_q, search_results=search_results)

    parsed_search_results = parse_search_results(search_results=search_results)
    finalized_prompt = search_prompt(search_results=parsed_search_results, q=original_q)
    logger.debug(f"finalized_prompt with search_results: {finalized_prompt}")
    return finalized_prompt
