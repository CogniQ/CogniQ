from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)


from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import system_message, user_message, CogniqOpenAI


class ChatGPT4(BasePersonality):
    def __init__(self, *, cslack: CogniqSlack, copenai: CogniqOpenAI):
        """
        Chat GPT4 personality
        Please call async_setup after initializing the personality.

        ```
        chat_gpt4 = ChatGPT4(cslack=cslack, copenai=copenai)
        await chat_gpt4.async_setup()
        ```

        Parameters:
        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.
        """
        self.cslack = cslack
        self.copenai = copenai

    async def async_setup(self) -> None:
        """
        Please call after initializing the personality.
        """
        pass

    async def ask_task(self, *, event: Dict, reply_ts: float, context: Dict) -> None:
        channel = event["channel"]
        message = event.get("text")
        if not message:
            logger.debug("I think the message was deleted. Ignoring.")
            return

        history = await self.cslack.openai_history.get_history(event=event, context=context)
        # logger.debug(f"history: {history}")

        ask_response = await self.ask(q=message, message_history=history, context=context)
        await self.cslack.chat_update(channel=channel, ts=reply_ts, context=context, text=ask_response["answer"])

    async def ask_directly(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        context: Dict[str, Any],
        stream_callback: Callable[..., None] | None = None,
        reply_ts: float | None = None,
    ) -> str:
        """
        Ask directly to the personality.
        """
        ask_response = await self.ask(q=q, message_history=message_history, stream_callback=stream_callback, context=context)
        return ask_response["answer"]

    async def ask(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        stream_callback: Callable[..., None] | None = None,
        context: Dict,
        reply_ts: float | None = None,
    ) -> Dict[str, Any]:
        if message_history is None:
            message_history = []
        # bot_id = await self.cslack.openai_history.get_bot_user_id(context=context)
        bot_name = await self.cslack.openai_history.get_bot_name(context=context)
        # logger.info(f"Answering: {q}")

        # if the history is too long, summarize it
        message_history = self.copenai.summarizer.ceil_history(message_history)

        # Set the system message
        message_history = [system_message(f"Hello, I am {bot_name}. I am a slack bot that can answer your questions.")] + message_history

        # if prompt is too long, summarize it
        short_q = await self.copenai.summarizer.ceil_prompt(q)

        logger.info("short_q: " + short_q)
        message_history.append(user_message(short_q))

        res = await self.copenai.async_chat_completion_create(
            messages=message_history,
            stream_callback=stream_callback,
            model="gpt-4",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        answer = res["choices"][0]["message"]["content"]
        logger.info(f"final_answer: {answer}")
        return {"answer": answer, "response": res}

    @property
    def description(self) -> str:
        return "I do not modify the query, and simply ask the question to ChatGPT 4."

    @property
    def name(self) -> str:
        return "ChatGPT4"
