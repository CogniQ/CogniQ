import logging

logger = logging.getLogger(__name__)

from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

import asyncio

from cogniq.personalities import (
    BingSearch,
    ChatGPT4,
    ChatAnthropic,
    Evaluator,
)


from config import config

import re


class MultiplePersonalities:
    def __init__(self, *, config):
        self.config = config

        # Initialize the slack bot
        self.cslack = CogniqSlack(
            config=config,
        )

        # Setup the personalities
        self.copenai = CogniqOpenAI(config=config)

        self.bing_search = BingSearch(
            config=config, cslack=self.cslack, copenai=self.copenai
        )

        self.chat_gpt4 = ChatGPT4(
            config=config, cslack=self.cslack, copenai=self.copenai
        )

        self.chat_anthropic = ChatAnthropic(
            config=config,
            cslack=self.cslack,
        )

        self.evaluator = Evaluator(
            config=config,
            cslack=self.cslack,
            copenai=self.copenai,
        )

        # Finally, register the app_mention and message events
        self.register_app_mention()
        self.register_message()

    async def start(self):
        """
        Starts one Slack bot instance, and multiple personalities.
        """
        await self.bing_search.async_setup()
        await self.chat_gpt4.async_setup()
        await self.chat_anthropic.async_setup()
        await self.evaluator.async_setup()
        await self.cslack.start()

    async def dispatch(self, *, event, say, original_ts):
        reply = await say(f"Let me figure that out...", thread_ts=original_ts)
        reply_ts = reply["ts"]

        # Text from the event
        text = event.get("text")
        # Dictionary with the module's wake patterns and corresponding ask tasks
        personalities = [
            self.bing_search,
            self.chat_gpt4,
        ]

        _evaluation_task = asyncio.create_task(self.evaluator.ask_task(event=event, reply_ts=reply_ts, personalities=personalities))

    def register_app_mention(self):
        @self.cslack.app.event("app_mention")
        async def handle_app_mention(event, say):
            logger.info(f"app_mention: {event.get('text')}")
            original_ts = event["ts"]
            await self.dispatch(event=event, say=say, original_ts=original_ts)

    def register_message(self):
        @self.cslack.app.event("message")
        async def handle_message_events(event, say):
            logger.info(f"message: {event.get('text')}")
            channel_type = event["channel_type"]
            if channel_type == "im":
                original_ts = event["ts"]
                await self.dispatch(event=event, say=say, original_ts=original_ts)
