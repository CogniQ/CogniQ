from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import asyncio

from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack

from .prompts import search_prompt, retrieval_augmented_prompt


class Ask:
    def __init__(
        self,
        *,
        config: dict,
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
        **kwargs,
    ):
        """
        Ask subclass of the ChatGPT4 personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, cslack=cslack, copenai=copenai)
        await ask.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat GPT4 personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.


        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.

        """

        self.config = config
        self.cslack = cslack
        self.copenai = copenai

    async def async_setup(self):
        """
        Call me after initialization, please!
        """
        self.bot_id = await self.cslack.openai_history.get_bot_user_id()
        self.bot_name = await self.cslack.openai_history.get_bot_name()

    async def ask(self, *, q, message_history=None):
        message_history = message_history or []

        # if the history is too long, summarize it
        message_history = self.copenai.summarizer.ceil_history(message_history)

        # Set the system message
        message_history = [
            system_message(
                f"Hello, I am {self.bot_name}. I am a slack bot that can answer your questions."
            )
        ] + message_history

        # if prompt is too long, summarize it
        short_q = await self.copenai.summarizer.ceil_prompt(q)

        my_search_prompt = search_prompt(q=short_q)

        search_prompt_history = message_history.copy() + [
            user_message(my_search_prompt)
        ]

        search_query_response = await self.copenai.async_chat_completion_create(
            messages=search_prompt_history,
            model=self.config["OPENAI_CHAT_MODEL"],  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        search_query = search_query_response["choices"][0]["message"]["content"]

        slack_search_response = await self.cslack.search.search_texts(q=search_query)

        # logger.info(f"slack_search_response: {slack_search_response}")

        prompt = retrieval_augmented_prompt(
            q=short_q, slack_search_response=slack_search_response
        )

        logger.info(f"Retrieval augmented prompt: {prompt}")

        # If prompt is too long, summarize it
        short_prompt = await self.copenai.summarizer.ceil_prompt(prompt)

        if prompt != short_prompt:
            logger.info(f"Original prompt: {prompt}")
            logger.info(f"Evaluating shortened prompt: {short_prompt}")
        else:
            logger.info(f"Evaluating prompt: {short_prompt}")

        message_history.append(user_message(prompt))

        answer = await self.copenai.async_chat_completion_create(
            messages=message_history,
            model=self.config["OPENAI_CHAT_MODEL"],  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        final_answer = answer["choices"][0]["message"]["content"]
        logger.info(f"final_answer: {final_answer}")
        return final_answer
