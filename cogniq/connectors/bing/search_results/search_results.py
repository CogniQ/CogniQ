from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .search_response import parse_search_response
from .news_response import parse_news_answer


def raise_error(*, search_results):
    e = search_results["errors"][0]
    raise Exception(f"Error performing search: {e.get('code')}: {e.get('message')}")


def parse_search_results(*, search_results):
    _type_to_parse_function = {
        "ErrorResponse": raise_error,
        "SearchResponse": parse_search_response,
        "News": parse_news_answer,
    }

    # logger.debug(f"search_results: {search_results}")

    type = search_results.get("_type")
    if type in _type_to_parse_function:
        parsed_items = _type_to_parse_function[type](search_results=search_results)
        return [to_text(item) for item in parsed_items]
    else:
        raise Exception(f"Unknown search result type: {type}")


def to_text(parsed_item):
    if parsed_item:
        return f"{parsed_item['snippet']} [{parsed_item['name']}]({parsed_item['url']})\n\n"
    else:
        return None
