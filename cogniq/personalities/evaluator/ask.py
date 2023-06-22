from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import asyncio

from cogniq.personalities import BaseAsk, BasePersonality
from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack

from .prompts import evaluator_prompt


class AskPersonality(TypedDict):
    personality: BasePersonality
    stream_callback: Callable[..., None] | None
    reply_ts: str | None


class Ask(BaseAsk):
    def __init__(
        self,
        *,
        config: Dict[str, str],
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

    async def async_setup(self) -> None:
        """
        Call me after initialization, please!
        """
        pass

    async def ask(
        self,
        *,
        q,
        message_history: List[dict[str, str]],
        ask_personalities: Dict[str, AskPersonality],
        context: Dict,
        stream_callback: Callable[..., None] | None = None,
    ) -> str:
        # bot_id = await self.cslack.openai_history.get_bot_user_id(context=context)

        bot_name = await self.cslack.openai_history.get_bot_name(context=context)

        # if the history is too long, summarize it
        message_history = self.copenai.summarizer.ceil_history(message_history)

        # Set the system message
        message_history = [system_message(f"Hello, I am {bot_name}. I am a slack bot that can answer your questions.")] + message_history

        # if prompt is too long, summarize it
        short_q = await self.copenai.summarizer.ceil_prompt(q)

        response_futures = []
        # Run the personalities
        for name, info in ask_personalities.items():
            personality = info['personality']
            stream_callback = info['stream_callback']
            reply_ts = info['reply_ts']
            response_future = asyncio.create_task(
                personality.ask_directly(
                    q=short_q, message_history=message_history, stream_callback=stream_callback, context=context, reply_ts=reply_ts
                )
            )
            response_futures.append((personality.description, response_future))

        # Wait for the futures to finish
        responses = await asyncio.gather(*(response_future for _, response_future in response_futures))
        responses_with_descriptions = [(description, response) for (description, _), response in zip(response_futures, responses)]

        # Log the responses
        for description, response in responses_with_descriptions:
            logger.debug(f"{description}: {response}")

        prompt = evaluator_prompt(q=short_q, responses_with_descriptions=responses_with_descriptions)

        # If prompt is too long, summarize it
        short_prompt = await self.copenai.summarizer.ceil_prompt(prompt)

        if prompt != short_prompt:
            logger.info(f"Original prompt: {prompt}")
            logger.info(f"Evaluating shortened prompt: {short_prompt}")
        else:
            logger.info(f"Evaluating prompt: {short_prompt}")

        message_history.append(user_message(short_prompt))

        answer = await self.copenai.async_chat_completion_create(
            messages=message_history,
            model="gpt-4",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        final_answer = answer["choices"][0]["message"]["content"]
        logger.info(f"final_answer: {final_answer}")
        return final_answer
