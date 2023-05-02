from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .common import system_message, user_message, assistant_message

from .async_chat_completion_create import async_chat_completion_create


async def get_retrieval_strategy(*, q, message_history=None, bot_id="CogniQ"):
    retrieval_message_history = [
        system_message(
            f"""
        I am {bot_id}, an retrieval augmentation expert that can determine the best strategy to apply for answering your question.
        The available strategies are:
        - "search: <the search query>": Search the web for the answer
        - "ask: <the question>": Ask the user for more information, and then provide the question to ask the user.
        - "none": No augmentation is necessary
        When asked, I will only respond with one of the above strategies.
        """
        ),
        user_message("How's the weather in New York?"),
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
