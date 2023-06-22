from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

from .ask import Ask


class SlackSearch(BasePersonality):
    def __init__(self, *, config: Dict[str, str], cslack: CogniqSlack, copenai: CogniqOpenAI, **kwargs):
        """
        SlackSearch personality
        Please call async_setup after initializing the personality.

        ```
        slack_search = SlackSearch(config=config, copenai=copenai)
        await slack_search.async_setup()
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

    async def ask_task(self, *, event: Dict, reply_ts: float, context: Dict) -> None:
        """
        Executes the ask_task against all the personalities and returns the best or compiled response.
        """
        channel = event["channel"]
        message = event["text"]

        message_history = await self.cslack.openai_history.get_history(event=event, context=context)
        openai_response = await self.ask.ask(
            q=message,
            context=context,
            message_history=message_history,
        )
        # logger.debug(openai_response)
        await self.cslack.chat_update(channel=channel, ts=reply_ts, context=context, text=openai_response)

    async def ask_directly(
        self, *, q, message_history: List[dict[str, str]], context: Dict, reply_ts: float | None = None, **kwargs
    ) -> str:
        """
        Ask directly to the personality.
        """
        response = await self.ask.ask(q=q, message_history=message_history, context=context, reply_ts=reply_ts, **kwargs)
        return response

    @property
    def description(self) -> str:
        return "I search Slack for relevant conversations."

    @property
    def name(self) -> str:
        return "Slack Search"
