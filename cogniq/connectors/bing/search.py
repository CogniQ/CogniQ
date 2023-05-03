from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_bing_search
from .search_results import parse_search_results


async def search(*, q, search_type):
    search_results = await async_bing_search(
        q=q, search_type=search_type, num_results=4
    )

    parsed_search_results = parse_search_results(search_results=search_results)
    return parsed_search_results
