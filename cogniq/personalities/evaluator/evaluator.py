from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import asyncio

from functools import partial

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

from .ask import Ask


class Buffer:
    def __init__(self):
        self.text = ""


class Evaluator(BasePersonality):
    def __init__(self, *, config: Dict[str, str], cslack: CogniqSlack, copenai: CogniqOpenAI, **kwargs):
        """
        Evaluator personality
        Please call async_setup after initializing the personality.

        ```
        evaluator = Evaluator(config=config, copenai=copenai)
        await evaluator.async_setup()
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

        self.ask = Ask(config=config, cslack=cslack, copenai=copenai)

    async def async_setup(self) -> None:
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event: Dict, reply_ts: float, personalities: List[BasePersonality], context: Dict) -> None:
        """
        Executes the ask_task against all the personalities and returns the best or compiled response.
        """
        buffer_post_timeout = 300  # seconds
        try:
            channel = event["channel"]
            message = event["text"]

            # create a buffer for each personality
            response_buffers = {p.name: Buffer() for p in personalities}
            for name, buf in response_buffers.items():
                buf.text += f"-------------------------\n{name} Stream of Thought:\n"

            buffer_post_end = asyncio.Event()

            def stream_callback(name: str, token: str, **kwargs) -> None:
                setattr(response_buffers[name], "text", response_buffers[name].text + token)

            # Wrap personalities and their callbacks in a dict of dicts
            ask_personalities = {
                p.name: {"personality": p, "stream_callback": partial(stream_callback, p.name), "reply_ts": reply_ts} for p in personalities
            }

            buffer_post_end = asyncio.Event()  # event flag for ending the buffer_and_post loop
            buffer_and_post_task = asyncio.create_task(
                self.buffer_and_post(
                    response_buffers=response_buffers,
                    channel=channel,
                    reply_ts=reply_ts,
                    context=context,
                    interval=1,
                    buffer_post_end=buffer_post_end,
                )
            )
            message_history = await self.cslack.openai_history.get_history(event=event, context=context)

            ask_response = {"answer": ""}
            ask_response = await asyncio.wait_for(
                self.ask.ask(
                    q=message,
                    message_history=message_history,
                    ask_personalities=ask_personalities,
                    context=context,
                ),
                buffer_post_timeout,
            )
        finally:
            buffer_post_end.set()  # end the buffer_and_post loop
            await buffer_and_post_task  # ensure buffer_and_post task is finished
            await self.cslack.chat_update(channel=channel, ts=reply_ts, text=ask_response["answer"], context=context)

    async def buffer_and_post(
        self, *, response_buffers: Dict, channel: str, reply_ts: float, context: Dict, interval: int, buffer_post_end: asyncio.Event
    ) -> None:
        while not buffer_post_end.is_set():
            combined_text = "\n".join(buf.text for buf in response_buffers.values())
            if combined_text:
                await self.cslack.chat_update(
                    channel=channel,
                    ts=reply_ts,
                    context=context,
                    text=combined_text,
                    retry_on_rate_limit=False,
                )
            await asyncio.sleep(interval)

    async def ask_directly(
        self, *, q: str, message_history: List[Dict[str, str]], personalities: List[BasePersonality], context: Dict, **kwargs
    ) -> str:
        """
        Ask directly to the personality.
        """
        ask_response = await self.ask.ask(q=q, message_history=message_history, personalities=personalities, context=context, **kwargs)
        return ask_response["answer"]

    @property
    def description(self) -> str:
        return "I evaluate the responses from the other personalities and return the best one."

    @property
    def name(self) -> str:
        return "Evaluator"
