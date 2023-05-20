from cogniq.slack import CogniqSlack

import asyncio
from cogniq.personalities import (
    bing_search,
    chat_gpt4,
    chat_anthropic,
)

import re


async def dispatch(*, event, say, original_ts, cslack):
    reply = await say(f"Let me figure that out...", thread_ts=original_ts)
    reply_ts = reply["ts"]

    # Text from the event
    text = event.get("text")

    # Dictionary with the module's wake patterns and corresponding ask tasks
    tasks = {
        bing_search.wake_pattern: bing_search.ask_task,
        chat_anthropic.wake_pattern: chat_anthropic.ask_task,
        chat_gpt4.wake_pattern: chat_gpt4.ask_task,
    }

    # Initialize the default task
    default_task = chat_gpt4.ask_task

    # Flag to check if any task was created
    task_created = False

    # Loop through the tasks dictionary
    for wake_pattern, ask_task in tasks.items():
        # If the wake pattern is found in the text
        if re.search(wake_pattern, text):
            # Create a new task for the corresponding ask task
            asyncio.create_task(ask_task(event=event, reply_ts=reply_ts, cslack=cslack))
            # Set the flag to True
            task_created = True

    # If no wake patterns match, run the default task
    if not task_created:
        asyncio.create_task(default_task(event=event, reply_ts=reply_ts, cslack=cslack))


def register_app_mention(*, cslack: CogniqSlack):
    @cslack.app.event("app_mention")
    async def handle_app_mention(event, say):
        cslack.logger.info(f"app_mention: {event.get('text')}")
        original_ts = event["ts"]
        await dispatch(event=event, say=say, original_ts=original_ts, cslack=cslack)


def register_message(*, cslack: CogniqSlack):
    @cslack.app.event("message")
    async def handle_message_events(event, say):
        cslack.logger.info(f"message: {event.get('text')}")
        channel_type = event["channel_type"]
        if channel_type == "im":
            original_ts = event["ts"]
            await dispatch(event=event, say=say, original_ts=original_ts, cslack=cslack)
