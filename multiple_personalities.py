from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

import asyncio

from cogniq.personalities import (
    BingSearch,
    ChatGPT4,
    ChatAnthropic,
)

from config import config

import re


class MultiplePersonalities:
    def __init__(self, *, config, logger):
        self.config = config
        self.logger = logger

        # Initialize the slack bot
        self.cslack = CogniqSlack(
            config=config,
            logger=logger,
        )

        # Setup the personalities
        self.copenai = CogniqOpenAI(config=config, logger=logger)

        self.bing_search = BingSearch(
            config=config, logger=logger, cslack=self.cslack, copenai=self.copenai
        )

        self.chat_gpt4 = ChatGPT4(
            config=config, logger=logger, cslack=self.cslack, copenai=self.copenai
        )

        self.chat_anthropic = ChatAnthropic(
            config=config,
            logger=logger,
            cslack=self.cslack,
        )

        # Finally, register the app_mention and message events
        self.register_app_mention()
        self.register_message()

    async def start(self):
        """
        Starts one Slack bot instance, and routes messages according to wake word.
        """
        await self.bing_search.async_setup()
        await self.chat_gpt4.async_setup()
        await self.chat_anthropic.async_setup()
        await self.cslack.start()

    async def dispatch(self, *, event, say, original_ts):
        reply = await say(f"Let me figure that out...", thread_ts=original_ts)
        reply_ts = reply["ts"]

        # Text from the event
        text = event.get("text")
        # Dictionary with the module's wake patterns and corresponding ask tasks
        tasks = {
            self.bing_search.wake_pattern(): self.bing_search.ask_task,
            self.chat_anthropic.wake_pattern(): self.chat_anthropic.ask_task,
            self.chat_gpt4.wake_pattern(): self.chat_gpt4.ask_task,
        }

        # Initialize the default task
        default_task = self.chat_gpt4.ask_task

        # Flag to check if any task was created
        task_created = False

        # Loop through the tasks dictionary
        for wake_pattern, ask_task in tasks.items():
            # If the wake pattern is found in the text
            if re.search(wake_pattern, text):
                # Create a new task for the corresponding ask task
                asyncio.create_task(ask_task(event=event, reply_ts=reply_ts))
                # Set the flag to True
                task_created = True

        # If no wake patterns match, run the default task
        if not task_created:
            asyncio.create_task(default_task(event=event, reply_ts=reply_ts))

    def register_app_mention(self):
        @self.cslack.app.event("app_mention")
        async def handle_app_mention(event, say):
            self.logger.info(f"app_mention: {event.get('text')}")
            original_ts = event["ts"]
            await self.dispatch(event=event, say=say, original_ts=original_ts)

    def register_message(self):
        @self.cslack.app.event("message")
        async def handle_message_events(event, say):
            self.logger.info(f"message: {event.get('text')}")
            channel_type = event["channel_type"]
            if channel_type == "im":
                original_ts = event["ts"]
                await self.dispatch(event=event, say=say, original_ts=original_ts)
