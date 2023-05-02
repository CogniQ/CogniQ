def parse_news(*, search_results, item):
    """https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/response-objects#newsanswer"""
    target_id = item["value"]["id"]
    result = next(
        iter(filter(lambda el: el.get("id") == target_id, search_results["news"]["value"])),
        None,
    )

    if result:
        parsed_result = {
            "name": result.get("name"),
            "snippet": result.get("description"),
            "url": result.get("url"),
        }
        return parsed_result
    else:
        return None


def parse_webpages(*, search_results, item):
    """https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/response-objects#webanswer"""
    target_id = item["value"]["id"]
    result = next(
        iter(
            filter(
                lambda el: el.get("id") == target_id, search_results["webPages"]["value"]
            )
        ),
        None,
    )

    if result:
        parsed_result = {
            "name": result.get("name"),
            "snippet": result.get("snippet"),
            "url": result.get("url"),
        }
        return parsed_result
    else:
        return None


def parse_search_response(*, search_results):
    """https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/response-objects#searchresponse"""
    answerType_to_parse_function = {
        "WebPages": parse_webpages,
        "News": parse_news,
    }

    parsed_items = [
        answerType_to_parse_function[item["answerType"]](
            search_results=search_results, item=item
        )
        for item in search_results["rankingResponse"]["mainline"]["items"]
        if item["answerType"] in answerType_to_parse_function
    ]
    return parsed_items
