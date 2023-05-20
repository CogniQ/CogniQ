from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from ..personalities.bing_search.config import Config
from .chat import system_message, user_message
from .api import async_chat_completion_create

import tiktoken

encoding = tiktoken.encoding_for_model(Config["OPENAI_CHAT_MODEL"])


def encode(text):
    return encoding.encode(text)


def count_tokens(text):
    simple_coerced_string = str(text)
    return len(encode(simple_coerced_string))


def ceil_history(message_history):
    simple_coerced_string = str(message_history)
    total_tokens = count_tokens(simple_coerced_string)
    max_tokens = Config["OPENAI_MAX_TOKENS_HISTORY"]

    while total_tokens > max_tokens:
        message_history.pop(0)
        simple_coerced_string = str(message_history)
        total_tokens = count_tokens(simple_coerced_string)

    return message_history


def ceil_retrieval(retrieval):
    simple_coerced_string = str(retrieval)
    total_tokens = count_tokens(simple_coerced_string)
    max_tokens = Config["OPENAI_MAX_TOKENS_RETRIEVAL"]

    while total_tokens > max_tokens:
        retrieval = retrieval[:-1]  # removed last message
        simple_coerced_string = str(retrieval)
        total_tokens = count_tokens(simple_coerced_string)

    return retrieval


async def ceil_prompt(prompt):
    simple_coerced_string = str(prompt)
    if count_tokens(simple_coerced_string) > Config["OPENAI_MAX_TOKENS_PROMPT"]:
        return await summarize_content(
            simple_coerced_string, Config["OPENAI_MAX_TOKENS_PROMPT"]
        )
    else:
        return prompt


async def summarize_content(content, max_tokens):
    response = await async_chat_completion_create(
        messages=[
            system_message(
                "Please summarize the following content within the token limit."
            ),
            user_message(content),
        ],
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0,
    )
    answer = response["choices"][0]["message"]["content"].strip()
    return answer
