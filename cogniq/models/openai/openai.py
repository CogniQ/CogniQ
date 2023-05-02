from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .async_chat_completion_create import async_chat_completion_create

from .common import system_message, user_message

from .retrieval_strategy import get_retrieval_strategy


# TODO: Token limit management
async def ask(*, q, message_history=None, context=[]):
    logger.info(f"Answering: {q}")
    if message_history is None:
        message_history = [
            system_message("Hello, I am CogniQ, your personal assistant.")
        ]
    retrieval_strategy = await get_retrieval_strategy(
        q=q
    )

    # if retrieval_strategy starts with "ask: ", then ask the user the remainder of the string
    if retrieval_strategy.startswith("ask: "):
        return f"{retrieval_strategy[5:]} Please rephrase the question with the answer." # TODO: Make this a bit more elegant in a future iteration. The bot should just enter a refinement loop.
    # if retrieval_strategy is "search", then search the web for the answer
    if retrieval_strategy.startswith("search: "):
        search_results = ""
        q = search_results + q
    
    message_history.append(user_message(q))
    response = await async_chat_completion_create(
        messages=message_history,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n\n###\n"],
    )
    # logger.debug(f"response: {response}")
    return (
        response["choices"][0]["message"]["content"]
    )
