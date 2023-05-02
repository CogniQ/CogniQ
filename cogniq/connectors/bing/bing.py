from langchain.utilities import BingSearchAPIWrapper
from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .config import Config

from cogniq.models.openai.best_search_result import get_best_search_result


bing = BingSearchAPIWrapper(bing_search_url=Config["BING_SEARCH_URL"], bing_subscription_key=Config["BING_SUBSCRIPTION_KEY"])

def search_prompt(*, search_results, q):
    return f"""
    {search_results}

    {q}
    """



async def search(*, q, original_q):
    search_results = bing.results(q, num_results=4)
    best_search_result = await get_best_search_result(q=original_q, search_results=search_results)

    finalized_prompt = search_prompt(search_results=search_results, q=original_q)
    logger.debug(f"finalized_prompt with search_results: {finalized_prompt}")
    return finalized_prompt