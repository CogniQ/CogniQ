from .webpage import parse_webpages
from .news import parse_news


def parse_search_results(results):
    answerType_to_parse_function = {
        "WebPages": parse_webpages,
        "News": parse_news,
    }

    if results.get("_type") == "ErrorResponse":
        e = results["errors"][0]
        raise Exception(f"Error performing search: {e.get('code')}: {e.get('message')}")

    parsed_items = [
        to_text(
            answerType_to_parse_function[item["answerType"]](results=results, item=item)
        )
        for item in results["rankingResponse"]["mainline"]["items"]
        if item["answerType"] in answerType_to_parse_function
    ]

    return parsed_items


def to_text(parsed_item):
    if parsed_item:
        return f"{parsed_item['snippet']} [{parsed_item['name']}]({parsed_item['url']})\n\n"
    else:
        return None
