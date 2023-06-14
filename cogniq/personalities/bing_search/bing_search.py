import logging

logger = logging.getLogger(__name__)

import re

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI


from .ask import Ask


class BingSearch(BasePersonality):
    def __init__(
        self,
        *,
        config: dict,
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
    ):
        """
        Bing Search personality

        Please call async_setup after initializing the personality.

        ```
        bing_search = BingSearch(config=config, cslack=cslack, copenai=copenai)
        await bing_search.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Bing Search personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.
            BING_SUBSCRIPTION_KEY (str): Bing subscription key.


        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.
        """

        self.config = config
        self.cslack = cslack
        self.copenai = copenai

        self.ask = Ask(config=config, cslack=cslack, copenai=copenai)

    async def async_setup(self):
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event: dict, reply_ts: int, context: dict):
        channel = event["channel"]
        message = event["text"]

        history = await self.cslack.openai_history.get_history(event=event)
        # logger.debug(f"history: {history}")

        answer, _agent_response = await self.ask.ask(q=message, message_history=history)
        # logger.debug(openai_response)
        await self.cslack.chat_update(channel=channel, ts=reply_ts, context=context, text=answer)

    async def ask_directly(
        self,
        *,
        q: str,
        message_history: list,
        stream_callback: callable = None,
        **kwargs,
    ):
        _answer, agent_response = await self.ask.ask(
            q=q,
            message_history=message_history,
            stream_callback=stream_callback,
            **kwargs,
        )
        transcript = agent_response["transcript"]
        transcript_summary = await self.copenai.summarizer.ceil_prompt(transcript)
        return transcript_summary

    @property
    def description(self):
        return "I perform extractive generation of answers from Bing search results."

    @property
    def name(self):
        return "Bing Search"
