from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import asyncio

from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack

from .prompts import evaluator_prompt


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

    async def ask(self, *, q, openai_history=None, anthropic_history=None, personalities):
        openai_history = openai_history or []
        anthropic_history = anthropic_history or ""

        # if the history is too long, summarize it
        openai_history = self.copenai.summarizer.ceil_history(openai_history)

        # Set the system message
        openai_history = [
            system_message(
                f"Hello, I am {self.bot_name}. I am a slack bot that can answer your questions."
            )
        ] + openai_history

        # if prompt is too long, summarize it
        short_q = await self.copenai.summarizer.ceil_prompt(q)

        response_futures = []
        # Run the personalities
        for personality in personalities:
            # TODO: detect whether the personality needs openai_history or anthropic_history. For now, only limit to openai_history
            response_future = asyncio.create_task(personality.ask_directly(q=short_q, message_history=openai_history))
            response_futures.append(response_future)

        # Wait for the futures to finish
        responses = await asyncio.gather(*response_futures)

        # Log the responses
        for response in responses:
            logger.debug(f"Evaluating candidate response: {response}")

        prompt = evaluator_prompt(q=short_q, responses=responses)

        logger.info (f"Evaluation prompt: {prompt}")

        openai_history.append(user_message(prompt))

        answer = await self.copenai.async_chat_completion_create(
            messages=openai_history,
            model="gpt-4",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        final_answer = answer["choices"][0]["message"]["content"]
        logger.info(f"final_answer: {final_answer}")
        return final_answer
