from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .async_chat_completion_create import async_chat_completion_create

from .common import system_message, user_message

from .retrieval_strategy import get_retrieval_strategy

from cogniq.connectors.bing import search


# TODO: Token limit management
async def ask(*, q, message_history=None, bot_id="CogniQ"):
    logger.info(f"Answering: {q}")
    if message_history is None:
        message_history = [
            system_message(f"Hello, I am {bot_id}, your personal assistant.")
        ]
    retrieval_strategy = await get_retrieval_strategy(
        q=q,
        bot_id=bot_id,
    )

    # if retrieval_strategy starts with "ask: ", then ask the user the remainder of the string
    if retrieval_strategy.startswith("ask: "):
        return f"{retrieval_strategy[5:]} Please rephrase the question with the answer." # TODO: Make this a bit more elegant in a future iteration. The bot should just enter a refinement loop.
    # if retrieval_strategy is "search", then search the web for the answer
    if retrieval_strategy.startswith("search: "):
        q = search(q=retrieval_strategy[8:], original_q=q)

    message_history.append(user_message(q))
    response = await async_chat_completion_create(
        messages=message_history,
        temperature=0.9,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n\n"],
    )
    # logger.debug(f"response: {response}")
    return (
        response["choices"][0]["message"]["content"]
    )
