from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from functools import singledispatchmethod

from .chat import system_message, user_message

import tiktoken


class Summarizer:
    def __init__(self, *, config: Dict, async_chat_completion_create: callable):
        """
        Summarizer is intended as a subclass of CogniqOpenAI and is responsible for managing context window.

        Parameters:
        config (dict): Configuration dictionary with the following keys:
            OPENAI_CHAT_MODEL (str): OpenAI model to use for chat.
            OPENAI_MAX_TOKENS_HISTORY (int): Context from chat history
            OPENAI_MAX_TOKENS_RETRIEVAL (int): Context from retrieval, such as Bing.
            OPENAI_MAX_TOKENS_PROMPT (int): The text that the user types will be summarized to this length if necessary.
            OPENAI_MAX_TOKENS_RESPONSE (int): Response from OpenAI.

        async_chat_completion_create (function): Function to create a chat completion.

        """
        self.config = config
        self.async_chat_completion_create = async_chat_completion_create

        self.encoding = tiktoken.encoding_for_model(self.config["OPENAI_CHAT_MODEL"])

    def encode(self, text: str) -> List[int]:
        return self.encoding.encode(text)

    @singledispatchmethod
    def count_tokens(self, text: Any) -> int:
        logger.error("Unsupported type passed to count_tokens: %s (%s)", type(text), text)
        raise TypeError(f"count_tokens does not support type {type(text)}: {text}")

    @count_tokens.register(str)
    def _(self, text: str) -> int:
        try:
            return len(self.encode(text))
        except TypeError as e:
            logger.error("ceil_history expects a string. Message: %s", text)
            raise e

    @count_tokens.register(list)
    def _(self, history: List[Dict[str, str]] | List[str]) -> int:
        """
        Count tokens in a list of OpenAI messages or a list of strings
        """
        if history and isinstance(history[0], dict) and "content" in history[0]:
            try:
                return sum(map(lambda x: self.count_tokens(x["content"]), history))
            except KeyError as e:
                logger.error("ceil_history expects an OpenAI formatted message history. Message history: %s", history)
                raise e
        elif history and isinstance(history[0], str):
            return sum(map(self.count_tokens, history))
        elif not history:
            return 0
        else:
            raise TypeError("count_tokens expects a list of OpenAI messages or a list of strings.")

    def ceil_history(self, message_history: List[Dict[str, str]], max_tokens: int | None = None) -> List[Dict[str, str]]:
        """
        Ceil the history to a maximum number of tokens.
        Removes entries from the BEGINNING of the history until the total number of tokens is less than max_tokens.
        """
        if max_tokens is None:
            max_tokens = self.config["OPENAI_MAX_TOKENS_HISTORY"]

        message_history_copy = message_history.copy()

        total_tokens = self.count_tokens(message_history_copy)

        while total_tokens > max_tokens:
            logger.debug("trimming ceil_history: total_tokens: %s", total_tokens)
            popped_message = message_history_copy.pop(0)
            total_tokens -= self.count_tokens([popped_message])

        return message_history_copy

    def ceil_retrieval(self, retrieval: List[str], max_tokens: int | None = None) -> List[str]:
        """
        Ceil the retrieval to a maximum number of tokens.
        Removes entries from the END of the retrieval until the total number of tokens is less than max_tokens.
        """
        if max_tokens is None:
            max_tokens = self.config["OPENAI_MAX_TOKENS_RETRIEVAL"]

        retrieval_copy = retrieval.copy()

        total_tokens = self.count_tokens(retrieval_copy)

        while total_tokens > max_tokens:
            retrieval_copy = retrieval_copy[:-1]  # removed last message
            total_tokens = self.count_tokens(retrieval_copy)

        return retrieval_copy

    async def ceil_prompt(self, prompt: str, max_tokens: int | None = None) -> str:
        if max_tokens is None:
            max_tokens = self.config["OPENAI_MAX_TOKENS_PROMPT"]

        simple_coerced_string = str(prompt)
        if self.count_tokens(simple_coerced_string) > max_tokens:
            return await self.summarize_content(simple_coerced_string, self.config["OPENAI_MAX_TOKENS_PROMPT"])
        else:
            return prompt

    async def summarize_content(self, content: str, max_tokens=None) -> str:
        if max_tokens is None:
            max_tokens = self.config["OPENAI_MAX_TOKENS_PROMPT"]
        content_length = self.count_tokens(content)
        remaining_context_window = self.config["OPENAI_TOTAL_MAX_TOKENS"] - max_tokens

        if content_length < max_tokens:
            return content

        if remaining_context_window < content_length:
            half = int(len(content) / 2)
            a = await self.summarize_content(content[0:half], max_tokens)
            b = await self.summarize_content(content[half:], max_tokens)
            return a + b

        response = await self.async_chat_completion_create(
            messages=[
                system_message("Please summarize the following content within the token limit."),
                user_message(content),
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0,
        )
        summary = response["choices"][0]["message"]["content"].strip()
        return summary
