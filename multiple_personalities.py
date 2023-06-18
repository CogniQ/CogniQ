from typing import *

import logging

logger = logging.getLogger(__name__)

import asyncio

from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI
from cogniq.personalities import (
    BingSearch,
    ChatGPT4,
    ChatAnthropic,
    SlackSearch,
    Evaluator,
)

from config import config


class MultiplePersonalities:
    def __init__(self, *, config):
        self.config = config

        # Initialize the slack bot
        self.cslack = CogniqSlack(
            config=config,
        )

        # Setup the personalities
        self.copenai = CogniqOpenAI(config=config)

        self.bing_search = BingSearch(config=config, cslack=self.cslack, copenai=self.copenai)

        self.chat_gpt4 = ChatGPT4(config=config, cslack=self.cslack, copenai=self.copenai)

        self.chat_anthropic = ChatAnthropic(
            config=config,
            cslack=self.cslack,
        )

        self.slack_search = SlackSearch(
            config=config,
            cslack=self.cslack,
            copenai=self.copenai,
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
        await self.slack_search.async_setup()
        await self.evaluator.async_setup()
        await self.cslack.start()

    async def first_response(self, *, context: dict, original_ts: str) -> Awaitable:
        """
        This method is called when the bot is called.
        """
        try:
            response = await context["say"](
                f"Let me figure that out...",
                thread_ts=original_ts,
            )
            return response
        except Exception as e:
            logger.error(e)
            raise e

    async def dispatch(self, *, event: dict, context: dict, original_ts: str) -> Awaitable:
        reply = await self.first_response(context=context, original_ts=original_ts)
        reply_ts = reply["ts"]

        # Text from the event
        text = event.get("text")
        # Dictionary with the module's wake patterns and corresponding ask tasks
        personalities = [
            self.chat_gpt4,
            self.bing_search,
            # self.chat_anthropic,
            self.slack_search,
        ]

        _evaluation_task = asyncio.create_task(
            self.evaluator.ask_task(
                event=event,
                reply_ts=reply_ts,
                personalities=personalities,
                context=context,
            )
        )

    def register_app_mention(self):
        @self.cslack.app.event("app_mention")
        async def handle_app_mention(event, context):
            logger.info(f"app_mention: {event.get('text')}")
            original_ts = event["ts"]
            await self.dispatch(event=event, context=context, original_ts=original_ts)

    def register_message(self):
        @self.cslack.app.event("message")
        async def handle_message_events(event, context):
            logger.info(f"message: {event.get('text')}")
            channel_type = event["channel_type"]
            if channel_type == "im":
                original_ts = event["ts"]
                await self.dispatch(event=event, context=context, original_ts=original_ts)
