from __future__ import annotations
from typing import *
import logging

logger = logging.getLogger(__name__)
import asyncio
from functools import partial

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import system_message, user_message, CogniqOpenAI

from .prompts import evaluator_prompt


class Buffer:
    def __init__(self):
        self.text = ""


class Evaluator(BasePersonality):
    @property
    def description(self) -> str:
        return "I evaluate the responses from the other personalities and return the best one."

    @property
    def name(self) -> str:
        return "Evaluator"

    async def ask_personalities_task(
        self, *, event: Dict[str, str], reply_ts: float, personalities: List[BasePersonality], context: Dict[str, Any]
    ) -> None:
        """
        Executes the ask_task against all the personalities and returns the best or compiled response.
        """
        buffer_post_timeout = 300  # seconds

        channel = event["channel"]
        q = event.get("text")
        if not q:
            logger.debug("I think the message was deleted. Ignoring.")
            return
        short_q = await self.copenai.summarizer.ceil_prompt(q)

        # create a buffer for each personality
        response_buffers = {p.name: Buffer() for p in personalities}
        for name, buf in response_buffers.items():
            buf.text += f"-------------------------\n{name} Stream of Thought:\n"

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
        message_history = await self.history(event=event, context=context)

        ask_response = {"answer": ""}
        try:
            ask_response = await asyncio.wait_for(
                self.ask_personalities(
                    q=short_q,
                    message_history=message_history,
                    personalities=ask_personalities,
                    context=context,
                ),
                buffer_post_timeout,
            )
        finally:
            buffer_post_end.set()  # end the buffer_and_post loop
            await buffer_and_post_task  # ensure buffer_and_post task is finished
            await self.cslack.chat_update(channel=channel, ts=reply_ts, text=ask_response["answer"], context=context)

    async def buffer_and_post(
        self,
        *,
        response_buffers: Dict,
        channel: str,
        reply_ts: float,
        context: Dict[str, Any],
        interval: int,
        buffer_post_end: asyncio.Event,
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

    async def ask(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        context: Dict[str, Any],
        stream_callback: Callable[..., None] | None = None,
        reply_ts: float | None = None,
    ) -> Dict[str, Any]:
        return {"answer": "This personality does not support asking directly. Please use the ask_personalities method.", "response": None}

    async def ask_personalities(
        self,
        *,
        q: str,
        message_history: List[dict[str, str]],
        context: Dict[str, Any],
        personalities: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        response_futures = []
        # Run the personalities
        for name, info in personalities.items():
            personality = info["personality"]
            stream_callback = info["stream_callback"]
            reply_ts = info["reply_ts"]
            response_future = asyncio.create_task(
                personality.ask_directly(
                    q=q, message_history=message_history, stream_callback=stream_callback, context=context, reply_ts=reply_ts
                )
            )
            response_futures.append((personality.description, response_future))

        # Wait for the futures to finish
        responses = await asyncio.gather(*(response_future for _, response_future in response_futures), return_exceptions=True)
        responses_with_descriptions = []

        for (description, _), response in zip(response_futures, responses):
            if isinstance(response, Exception):
                logger.exception(f"Exception while running {name}: {response}")
            else:
                responses_with_descriptions.append((description, response))

        # Log the responses
        for description, response in responses_with_descriptions:
            logger.debug(f"{description}: {response}")

        prompt = evaluator_prompt(q=q, responses_with_descriptions=responses_with_descriptions)

        # If prompt is too long, summarize it
        short_prompt = await self.copenai.summarizer.ceil_prompt(prompt)

        if prompt != short_prompt:
            logger.info(f"Original prompt: {prompt}")
            logger.info(f"Evaluating shortened prompt: {short_prompt}")
        else:
            logger.info(f"Evaluating prompt: {short_prompt}")

        message_history.append(user_message(short_prompt))

        response = await self.copenai.async_chat_completion_create(
            messages=message_history,
            model="gpt-4",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        answer = response["choices"][0]["message"]["content"]
        logger.info(f"answer: {answer}")
        return {"answer": answer, "response": response}
