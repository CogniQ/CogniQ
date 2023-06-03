from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

import re

from .ask import Ask


class Evaluator(BasePersonality):
    def __init__(
        self, *, config: dict, cslack: CogniqSlack, copenai: CogniqOpenAI, **kwargs
    ):
        """
        Evaluator personality
        Please call async_setup after initializing the personality.

        ```
        evaluator = Evaluator(config=config, copenai=copenai)
        await evaluator.async_setup()
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

    async def ask_task(self, *, event, reply_ts, personalities):
        """
        Executes the ask_task against all the personalities and returns the best or compiled response.
        """
        channel = event["channel"]
        message = event["text"]

        openai_history = await self.cslack.openai_history.get_history(event=event)
        anthropic_history = await self.cslack.anthropic_history.get_history(event=event)
        openai_response = await self.ask.ask(q=message, openai_history=openai_history, anthropic_history=anthropic_history, personalities=personalities)
        # logger.debug(openai_response)
        await self.cslack.app.client.chat_update(
            channel=channel, ts=reply_ts, text=openai_response
        )

    async def ask_directly(self, *, q, openai_history, anthropic_history, personalities, **kwargs):
        """
        Ask directly to the personality.
        """
        response = await self.ask.ask(q=q, openai_history=openai_history, anthropic_history=anthropic_history, personalities=personalities, **kwargs)
        return response