from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from wandb.sdk.data_types.trace_tree import Trace

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack

from .ask import Ask


class ChatAnthropic(BasePersonality):
    def __init__(self, *, config: Dict[str, str], cslack: CogniqSlack, **kwargs):
        """
        Chat Anthropic personality
        Please call async_setup after initializing the personality.

        ```
        chat_anthropic = ChatAnthropic(config=config, cslack=cslack)
        await chat_anthropic.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat Anthropic personality with the following keys:



        cslack (CogniqSlack): CogniqSlack instance.
        """

        self.config = config
        self.cslack = cslack

        self.ask = Ask(config=config, cslack=cslack)

    async def async_setup(self) -> None:
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event: Dict, reply_ts: float, context: Dict, parent_span: Trace) -> None:
        channel = event["channel"]
        message = event["text"]

        history = await self.cslack.anthropic_history.get_history(event=event, context=context)
        logger.debug(f"history: {history}")

        ask_response = await self.ask.ask(q=message, message_history=history, parent_span=parent_span)
        await self.cslack.chat_update(channel=channel, ts=reply_ts, context=context, text=ask_response["answer"])

    async def ask_directly(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        stream_callback: Callable[..., None] | None = None,
        context: Dict,
        reply_ts: float | None = None,
        parent_span: Trace,
    ) -> str:
        """
        Ask directly to the personality.
        """
        # Convert the message history from OpenAI to Anthropic format
        message_history = self.cslack.anthropic_history.openai_to_anthropic(message_history=message_history)
        ask_response = await self.ask.ask(q=q, message_history=message_history, parent_span=parent_span)
        return ask_response["answer"]

    @property
    def description(self) -> str:
        return "I do not modify the query. I simply ask the question to Anthropic Claude."

    @property
    def name(self) -> str:
        return "Anthropic Claude"
