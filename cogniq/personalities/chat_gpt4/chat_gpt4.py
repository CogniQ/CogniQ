from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

import re

from .ask import Ask


class ChatGPT4(BasePersonality):
    def __init__(
        self, *, config: dict, cslack: CogniqSlack, copenai: CogniqOpenAI, **kwargs
    ):
        """
        Chat GPT4 personality
        Please call async_setup after initializing the personality.

        ```
        chat_gpt4 = ChatGPT4(config=config, cslack=cslack, copenai=copenai)
        await chat_gpt4.async_setup()
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

    async def ask_directly(self, *, q, message_history, **kwargs):
        """
        Ask directly to the personality.
        """
        response = await self.ask.ask(q=q, message_history=message_history, **kwargs)
        return response

    @property
    def description(self):
        return "I do not modify the query, and simply ask the question to ChatGPT 4."
