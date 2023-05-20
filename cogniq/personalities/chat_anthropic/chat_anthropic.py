from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack

import logging
import re

from .ask import Ask


class ChatAnthropic(BasePersonality):
    def __init__(self, *, config: dict, logger: logging, cslack: CogniqSlack, **kwargs):
        """
        Chat Anthropic personality
        Please call async_setup after initializing the personality.

        ```
        chat_anthropic = ChatAnthropic(config=config, logger=logger, cslack=cslack)
        await chat_anthropic.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat Anthropic personality with the following keys:


        logger (logging.Logger): Logger to log information about the app's status.
        cslack (CogniqSlack): CogniqSlack instance.
        """
        self.logger = logger
        self.config = config
        self.cslack = cslack

        self.ask = Ask(config=config, logger=logger, cslack=cslack)
        self._wake_pattern = re.compile(r"\b(anthropic|claude)\b", re.IGNORECASE)

    async def async_setup(self):
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event, reply_ts):
        channel = event["channel"]
        message = event["text"]

        history = await self.cslack.anthropic_history.get_history(event=event)
        self.logger.debug(f"history: {history}")

        response = await self.ask.ask(q=message, message_history=history)
        await self.cslack.app.client.chat_update(
            channel=channel, ts=reply_ts, text=response
        )

    def wake_pattern(self):
        return self._wake_pattern
