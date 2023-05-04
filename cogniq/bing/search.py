from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_bing_search
from .parse import parse_search_results

async def search_results(*, q, search_type):
    search_results = await async_bing_search(
        q=q, search_type=search_type, num_results=4
    )
    return search_results

async def search_enhanced_prompt(*, q, search_type):
    return parse_search_results(search_results=search_results(q=q, search_type=search_type))