from langchain.utilities import BingSearchAPIWrapper
from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .config import Config


bing = BingSearchAPIWrapper(bing_search_url=Config["BING_SEARCH_URL"], bing_subscription_key=Config["BING_SUBSCRIPTION_KEY"])

def search_prompt(*, search_results, q):
    return f"""
    Given the following search results, what is the best answer to the following prompt?

    Search Results: {search_results}

    Prompt: {q}
    """

def search(*, q, original_q):
    search_results = bing.run(q)
    logger.debug(f"search_results: {search_results}")
    return search_prompt(search_results=search_results, q=original_q)