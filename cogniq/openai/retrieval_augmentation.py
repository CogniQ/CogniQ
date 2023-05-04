from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_chat_completion_create
from .chat import system_message, user_message, assistant_message
from .config import Config
from cogniq.bing import get_search_results_as_text

import re
import asyncio


def retrieval_augmented_prompt(*, search_web, search_news, q):
    return f"""Please answer the Query based on the below Contexts.

    Use Slack formatting (Markdown) to make your answer easier to read.

    Links have a different format, however. Example: <https://www.google.com|Google>.
    Cite your sources.

    Do not start your response with "According to the context provided..." or similar mentions of the context provided. Simply quote the context directly.
    Do not start your response with "As an AI language model,". In fact, don't mention the AI language model at all.

    Web Search Context: {search_web}

    News Search Context: {search_news}

    Query: {q}"""


async def filter_search_results(*, q, message_history, search_results):
    messages = [
        system_message(f"I am filtering the Context to eliminate irrelevant content."),
        user_message(f"""
    Please remove any irrelevant content from the Context so that I can best answer the Query.
    In particular, remove advertisements unrelated to the Query.
    Never modify any links.
    
    Context: {search_results}

    Query: {q}
    
    Filtered Context:""")
    ]

    # logger.debug(f"filter_search_results_prompt: {prompt}")
    response = await async_chat_completion_create(
        messages=messages,
        temperature=0.1,
        max_tokens=Config["OPENAI_MAX_TOKENS_RETRIEVAL"],
        top_p=1,
        frequency_penalty=0,  # scales down the log probabilities of words that the model has seen frequently during training
        presence_penalty=0,  # modifies the probability distribution to make less likely words that were present in the input prompt or seed text
    )
    answer = response["choices"][0]["message"]["content"].strip()
    # logger.debug(f"filtered_search_results: {answer}")
    return answer


async def get_retrieval_augmented_prompt(*, q, message_history, bot_id):
    # start the two search requests concurrently
    search_news_task = get_search_results_as_text(q=q, search_type="news")
    search_web_task = get_search_results_as_text(q=q, search_type="web")

    # wait for both search requests to complete
    search_news, search_web = await asyncio.gather(search_news_task, search_web_task)

    # start the two filtering requests concurrently
    filter_search_news_task = filter_search_results(
        q=q, message_history=message_history, search_results=search_news
    )
    filter_search_web_task = filter_search_results(
        q=q, message_history=message_history, search_results=search_web
    )

    # wait for both filtering requests to complete
    filtered_search_news, filtered_search_web = await asyncio.gather(
        filter_search_news_task, filter_search_web_task
    )

    return retrieval_augmented_prompt(
        q=q, search_news=filtered_search_news, search_web=filtered_search_web
    )
