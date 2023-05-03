from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_chat_completion_create

from .common import system_message, user_message

from .retrieval_strategy import get_retrieval_strategy

from cogniq.connectors.bing import search

import re

from .summarize_content import ceil_history, ceil_retrieval, ceil_prompt

from .config import Config


def retrieval_augmented_prompt(*, search_results, q):
    return f"""
    Context: {search_results}

    Please answer the Query based on the above Context. 
    If provided in the Context, include relevant links in your response, nicely formatted for Slack. Example: <https://www.google.com|Google>.
    
    Only include links if they are directly provided in the Context. Do not generate new links or use links not mentioned in the Context.
    Do not start your response with "According to the context provided...".

    Query: {q}
    """


async def ask(*, q, message_history=None, bot_id="CogniQ"):
    logger.info(f"Answering: {q}")
    if message_history is None:
        message_history = [
            system_message(f"Hello, I am {bot_id}, your personal assistant.")
        ]

    # if the history is too long, summarize it
    message_history = await ceil_history(message_history)

    retrieval_strategy = await get_retrieval_strategy(
        q=q,
        bot_id=bot_id,
    )

    logger.info(f"retrieval_strategy: {retrieval_strategy}")
    # if retrieval_strategy starts with "ask: ", then ask the user the remainder of the string
    if retrieval_strategy.startswith("ask: "):
        return f"{retrieval_strategy[5:]} Please rephrase the question with the answer."  # TODO: Make this a bit more elegant in a future iteration. The bot should just enter a refinement loop.

    # if retrieval_strategy is "search", then search the web for the answer
    if retrieval_strategy.startswith("search: "):
        pattern = r"search:\s(\w+):\s(.*)$"
        match = re.match(pattern, retrieval_strategy)
        search_type = match.group(1)
        search_query = match.group(2)
        # logger.debug(f"search_type: {search_type}, search_query: {search_query}")
        retrieval = await search(q=search_query, search_type=search_type)

    # if retrieval is too long, summarize it.
    retrieval = await ceil_retrieval(retrieval)

    # if prompt is too long, summarize it
    q = await ceil_prompt(q)

    q = retrieval_augmented_prompt(search_results=retrieval, q=q)

    message_history.append(user_message(q))
    logger.info(f"asking question: {q}")
    response = await async_chat_completion_create(
        messages=message_history,
        temperature=0.5,
        max_tokens=Config["OPENAI_MAX_TOKENS_RESPONSE"],
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
    )
    logger.debug(f"response: {response}")
    return response["choices"][0]["message"]["content"]
