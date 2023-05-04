from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_chat_completion_create

from .common import system_message, user_message

from .retrieval_strategy import get_retrieval_strategy

from cogniq.bing import search_enhanced_prompt

import re

from .summarize_content import ceil_history, ceil_retrieval, ceil_prompt

from .config import Config


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
    retrieval = None

    # if retrieval_strategy is "search", then search the web for the answer
    if retrieval_strategy.startswith("search: "):
        pattern = r"search:\s(\w+):\s(.*)$"
        match = re.match(pattern, retrieval_strategy)
        search_type = match.group(1)
        search_query = match.group(2)
        # logger.debug(f"search_type: {search_type}, search_query: {search_query}")
        retrieval = await search_enhanced_prompt(
            q=search_query, search_type=search_type
        )

    # if retrieval is too long, summarize it.
    retrieval = await ceil_retrieval(retrieval)

    # if prompt is too long, summarize it
    q = await ceil_prompt(q)

    q = retrieval_augmented_prompt(search_results=retrieval, q=q)

    message_history.append(user_message(q))
    logger.info(f"asking question: {q}")
    response = await async_chat_completion_create(
        messages=message_history,
        temperature=0.9,
        max_tokens=Config["OPENAI_MAX_TOKENS_RESPONSE"],
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
    )
    logger.debug(f"response: {response}")
    return response["choices"][0]["message"]["content"]
