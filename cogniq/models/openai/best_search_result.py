from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .common import system_message, user_message, assistant_message

from .async_chat_completion_create import async_chat_completion_create


async def get_best_search_result(
    *, q, message_history=None, search_results=None, bot_id="CogniQ"
):
    retrieval_message_history = [
        system_message(
            f"""
        I am {bot_id}, an retrieval augmentation expert that can determine the best search result for answering your question.
        Respond with the best search result for the question.
        """
        ),
        user_message("""
            [
                {
                    "snippet": "Stock Market &amp; <b>Finance</b> <b>News</b> - Wall Street Journal MOVERS: Apr 27 &#39;23 4:00 PM ET Heard on the Street Heard on the Street: GDP Report’s Bright Side The recession so many investors are expecting...",
                    "title": "Stock Market &amp; Finance News - Wall Street Journal",
                    "link": "https://www.wsj.com/news/markets",
                },
                {
                    "snippet": "<b>Finance</b> UBS looks to bring Naratil back and mulls Swiss bank spin-off, NZZ am Sonntag reports April 30, 2023 <b>Finance</b> FDIC prepares to place First Republic under receivership April 29, 2023...",
                    "title": "Latest Finance News | Today&#39;s Top Headlines | Reuters",
                    "link": "https://www.reuters.com/business/finance/",
                },
                {
                    "snippet": "<b>Finance</b> This is First Republic’s plan to avoid a U.S. government takeover Wed, Apr 26th 2023 Fast Money ‘The hard money is now,’ Stifel’s chief strategist warns Tue, Apr 25th 2023 Market Insider...",
                    "title": "Finance News - CNBC",
                    "link": "https://www.cnbc.com/finance/",
                },
                {
                    "snippet": "8:06a Treasury yields ease as investors await Fed’s favorite inflation indicator 7:54a Cumulus Media stock price target cut to $10 from $16 at B. Riley Barron&#39;s Big Oil&#39;s Profits Are Strong. Lower...",
                    "title": "MarketWatch: Stock Market News - Financial News - MarketWatch",
                    "link": "https://www.marketwatch.com/",
                },
            ]

            What's happening with First Republic?
        """),
        assistant_message("search: Weather in New York today\n"),
        user_message("How's the weather?"),
        assistant_message("ask: What city?\n"),
        user_message("What is the plot of Macbeth?"),
        assistant_message("none\n"),
        user_message("What movies are showing today in Los Angeles?"),
        assistant_message("search: Movies showing today in Los Angeles\n"),
        user_message(q),
    ]


    if message_history is None:
        my_message_history = retrieval_message_history
    else:
        my_message_history = message_history.copy()
        my_message_history.extend(retrieval_message_history)

    response = await async_chat_completion_create(
        messages=my_message_history,
        temperature=0.3,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n"],
    )
    strategy = response["choices"][0]["message"]["content"]
    logger.info(f"retrieval strategy: {strategy}")
    return strategy
