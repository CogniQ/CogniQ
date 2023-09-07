from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

from .ask import Ask


class SlackSearch(BasePersonality):
    def __init__(self, *, cslack: CogniqSlack, copenai: CogniqOpenAI):
        """
        SlackSearch personality
        Please call async_setup after initializing the personality.

        ```
        slack_search = SlackSearch(copenai=copenai)
        await slack_search.async_setup()
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

    async def ask_task(self, *, event: Dict, reply_ts: float, context: Dict) -> None:
        """
        Executes the ask_task against all the personalities and returns the best or compiled response.
        """
        channel = event["channel"]
        message = event["text"]

        message_history = await self.cslack.openai_history.get_history(event=event, context=context)
        ask_response = await self.ask.ask(
            q=message,
            context=context,
            message_history=message_history,
        )
        # logger.debug(openai_response)
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
        ask_response = await self.ask.ask(q=q, message_history=message_history, context=context, reply_ts=reply_ts)
        return ask_response["answer"]

    @property
    def description(self) -> str:
        return "I search Slack for relevant conversations."

    @property
    def name(self) -> str:
        return "Slack Search"
