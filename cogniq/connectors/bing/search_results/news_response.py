def parse_news(news_article):
    """https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/response-objects#newsarticle"""
    parsed_result = {
        "name": news_article.get("name"),
        "snippet": news_article.get("description"),
        "url": news_article.get("url"),
    }
    return parsed_result


def parse_news_answer(*, search_results):
    """https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/response-objects#newsanswer"""
    news_answer = search_results  # Translate from the calling dynamic function.
    parsed_items = [parse_news(item) for item in news_answer["value"]]
    return parsed_items
