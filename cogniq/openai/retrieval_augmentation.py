from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_completion_create
from .config import Config
from .summarize_content import ceil_retrieval
from cogniq.bing import get_search_results_as_text

import re



def retrieval_augmented_prompt(*, search_results, q):
    return f"""
    Context: {search_results}

    Please answer the Query based on the above Context. 
    
    Use Slack formatting (Markdown) to make your answer easier to read.

    Links have a different format, however. Example: <https://www.google.com|Google>.
    Cite your sources.

    Do not start your response with "According to the context provided..." or similar mentions of the context provided. Simply quote the context directly.
    Do not start your response with "As an AI language model,". In fact, don't mention the AI language model at all.

    Query: {q}
    """


async def get_retrieval_strategy(*, q, message_history=None, bot_id="CogniQ"):
    prompt = f"""
    I am {bot_id}, an retrieval augmentation expert that can determine the best strategy to apply for answering your question.
    The available strategies are:
    - "search: web: <the search query>": google for the answer
    - "search: news: <the search query>": Search news for the answer
    - "none": No augmentation is necessary
    When asked, I will only respond with one of the above strategies.

    Q: How's the weather in New York?
    A: search: news: How's the weather in New York?

    Q: What is the plot of Macbeth?
    A: search: web: What is the plot of Macbeth?

    Q: What movies are showing today in Los Angeles?
    A: search: news: Movies showing today in Los Angeles

    Q: What is the capital of France?
    A: search: web: What is the capital of France

    Q: How do you make a cake?
    A: search: web: How do you make a cake?

    Q: Give me a summary of this chat.
    A: none
    
    Q: summarize this thread.
    A: none

    Q: the winner of the NBA Finals
    A: search: news: the winner of the NBA Finals

    Q: {q}
    A:"""

    response = await async_completion_create(
        model="davinci",
        prompt=prompt,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n"],
    )
    strategy = response["choices"][0]["text"].strip()
    logger.info(f"retrieval strategy: {strategy}")
    return strategy


async def get_retrieval_augmented_prompt(*, q, message_history, bot_id):
    retrieval_strategy = await get_retrieval_strategy(
        q=q,
        bot_id=bot_id,
    )
    retrieval = None

    # if retrieval_strategy is "search", then search the web for the answer
    if retrieval_strategy.startswith("search: "):
        pattern = r"search:\s(\w+):\s(.*)$"
        match = re.match(pattern, retrieval_strategy)
        search_type = match.group(1)
        search_query = match.group(2)
        # logger.debug(f"search_type: {search_type}, search_query: {search_query}")
        retrieval = await get_search_results_as_text(
            q=search_query, search_type=search_type
        )

    # if retrieval is too long, summarize it.
    retrieval = ceil_retrieval(retrieval)

    return retrieval_augmented_prompt(q=q, search_results=retrieval)
