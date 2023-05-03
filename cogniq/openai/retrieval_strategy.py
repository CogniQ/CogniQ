from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_completion_create


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
