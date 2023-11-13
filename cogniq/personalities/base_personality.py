from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod

from cogniq.slack import CogniqSlack
from cogniq.openai import system_message, user_message, CogniqOpenAI


class BasePersonality(ABC):
    def __init__(self, cslack: CogniqSlack, copenai: CogniqOpenAI):
        """
        Initialize the BasePersonality.
        :param cslack: CogniqSlack instance.
        """
        self.cslack = cslack
        self.copenai = copenai

    @property
    @abstractmethod
    def description(self) -> str:
        """
        A short description of the personality. This is used by an evaluator to note the context of the response.
        :return: The description of the personality.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the personality.
        :return: The name of the personality.
        """
        pass

    async def async_setup(self) -> None:
        """
        Perform any asynchronous setup tasks that are necessary for the personalityto function properly.
        """
        pass

    async def history(self, *, event: Dict[str, str], context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Returns the history of the event.
        """
        return await self.cslack.openai_history.get_history(event=event, context=context)

    async def ask_task(self, *, event: Dict[str, str], reply_ts: float, context: Dict[str, Any], thread_ts: str, **kwargs) -> None:
        channel = event["channel"]
        message = event.get("text")
        if not message:
            logger.debug("I think the message was deleted. Ignoring.")
            return

        history = await self.cslack.openai_history.get_history(event=event, context=context)
        # logger.debug(f"history: {history}")

        ask_response = await self.ask(q=message, message_history=history, context=context, reply_ts=reply_ts, thread_ts=thread_ts)
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
        ask_response = await self.ask(
            q=q, message_history=message_history, context=context, stream_callback=stream_callback, reply_ts=reply_ts
        )
        return ask_response["answer"]

    @abstractmethod
    async def ask(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        context: Dict[str, Any],
        stream_callback: Callable[..., None] | None = None,
        reply_ts: float | None = None,
        thread_ts: str | None = None,
    ) -> Dict[str, Any]:
        """
        Ask a question to the personality.
        """
        pass
