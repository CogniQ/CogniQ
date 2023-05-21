from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

import logging
import re

from .ask import Ask


class BingSearch(BasePersonality):
    def __init__(
        self,
        *,
        config: dict,
        logger: logging.Logger,
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
    ):
        """
        Bing Search personality

        Please call async_setup after initializing the personality.

        ```
        bing_search = BingSearch(config=config, logger=logger, cslack=cslack, copenai=copenai)
        await bing_search.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Bing Search personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.
            BING_SUBSCRIPTION_KEY (str): Bing subscription key.

        logger (logging.Logger): Logger to log information about the app's status.
        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.
        """
        self.logger = logger
        self.config = config
        self.cslack = cslack
        self.copenai = copenai

        self.ask = Ask(config=config, logger=logger, cslack=cslack, copenai=copenai)
        self._wake_pattern = re.compile(
            r"\b(search|bing|websearch|google)\b", re.IGNORECASE
        )

    async def async_setup(self):
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event, reply_ts):
        channel = event["channel"]
        message = event["text"]

        history = await self.cslack.openai_history.get_history(event=event)
        # logger.debug(f"history: {history}")

        openai_response = await self.ask.ask(q=message, message_history=history)
        # logger.debug(openai_response)
        await self.cslack.app.client.chat_update(
            channel=channel, ts=reply_ts, text=openai_response
        )

    def wake_pattern(self):
        return self._wake_pattern