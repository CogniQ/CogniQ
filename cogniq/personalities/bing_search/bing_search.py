from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI


from .ask import Ask


class BingSearch(BasePersonality):
    def __init__(
        self,
        *,
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
    ):
        """
        Bing Search personality

        Please call async_setup after initializing the personality.

        ```
        bing_search = BingSearch(cslack=cslack, copenai=copenai)
        await bing_search.async_setup()
        ```

        Parameters:
        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.
        """

        self.cslack = cslack
        self.copenai = copenai

        self.ask = Ask(cslack=cslack, copenai=copenai)

    async def async_setup(self) -> None:
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event: Dict, reply_ts: float, context: Dict, **kwargs) -> None:
        channel = event["channel"]
        message = event["text"]

        history = await self.cslack.openai_history.get_history(event=event, context=context)
        # logger.debug(f"history: {history}")

        ask_response = await self.ask.ask(q=message, message_history=history, context=context)
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
        ask_response = await self.ask.ask(
            q=q,
            message_history=message_history,
            stream_callback=stream_callback,
            **kwargs,
        )
        transcript = ask_response["response"]["transcript"]
        transcript_summary = await self.copenai.summarizer.ceil_prompt(transcript)
        return transcript_summary

    @property
    def description(self) -> str:
        return "I perform extractive generation of answers from Bing search results."

    @property
    def name(self) -> str:
        return "Bing Search"
