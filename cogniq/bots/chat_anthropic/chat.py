from cogniq.logging import setup_muted_logger

logger = setup_muted_logger(__name__)

from .config import Config

from cogniq.slack import CogniqSlack

from .ask import ask_task
import asyncio


def register_app_mention(*, cslack: CogniqSlack):
    @cslack.app.event("app_mention")
    async def handle_app_mention(event, say):
        cslack.logger.info(f"app_mention: {event.get('text')}")
        original_ts = event["ts"]
        reply = await say(f"Let me figure that out...", thread_ts=original_ts)
        reply_ts = reply["ts"]
        asyncio.create_task(ask_task(event=event, reply_ts=reply_ts, cslack=cslack))


def register_message(*, cslack: CogniqSlack):
    @cslack.app.event("message")
    async def handle_message_events(event, say):
        cslack.logger.info(f"message: {event.get('text')}")
        channel_type = event["channel_type"]
        if channel_type == "im":
            original_ts = event["ts"]
            reply = await say(f"Let me figure that out...", thread_ts=original_ts)
            reply_ts = reply["ts"]
            asyncio.create_task(ask_task(event=event, reply_ts=reply_ts, cslack=cslack))


async def start(config=Config):
    """
    Starts the CogniqSlack application.

    Args:
        config (dict, optional): Configuration for the Slack app. Defaults to Config. Pass in config when you have multiple instances.
        logger (logging.Logger): Logger object for logging application status.
    """
    await CogniqSlack(
        config=config,
        logger=logger,
        register_functions=[register_app_mention, register_message],
    ).start()
