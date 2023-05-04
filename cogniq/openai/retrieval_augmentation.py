from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_chat_completion_create
from .chat import system_message, user_message, assistant_message
from .config import Config
from cogniq.bing import get_search_results_as_text

import re
import asyncio


def retrieval_augmented_prompt(*, search_web, search_news, q):
    return f"""I have just now performed a search for "{q}" on Bing Web Search and Bing News Search. 
    
    Help me answer the Query by selecting the most relevant content from the Context. 
    You may add additional germane content to the Context.

    Use Slack formatting (Markdown) to make your answer easier to read.

    Links have a different format, however. Example: <https://www.google.com|Google>.
    Cite your sources.

    Do not start your response with "According to the context provided..." or similar mentions of the context provided. Simply quote the context directly.
    Do not start your response with "As an AI language model,". In fact, don't mention the AI language model at all.

    Web Search Context: {search_web}

    News Search Context: {search_news}

    Query: {q}"""


async def get_retrieval_augmented_prompt(*, q, message_history, bot_id):
    # start the two search requests concurrently
    search_news_task = get_search_results_as_text(q=q, search_type="news")
    search_web_task = get_search_results_as_text(q=q, search_type="web")

    # wait for both search requests to complete
    search_news, search_web = await asyncio.gather(search_news_task, search_web_task)

    return retrieval_augmented_prompt(
        q=q, search_news=search_news, search_web=search_web
    )
