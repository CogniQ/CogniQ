from cogniq.logging import setup_muted_logger

logger = setup_muted_logger(__name__)

from slack_bolt.async_app import AsyncApp
from .config import Config
from .app_mention import register_app_mention
from .message import register_message

import asyncio


app = AsyncApp(
    token=Config["SLACK_BOT_TOKEN"],
    signing_secret=Config["SLACK_SIGNING_SECRET"],
    logger=logger,
)

registration_config = {"app": app}

register_app_mention(**registration_config)
register_message(**registration_config)


async def devstart():
    from slack_bolt.adapter.socket_mode.aiohttp import (
        AsyncSocketModeHandler,
    )

    handler = AsyncSocketModeHandler(app, Config["SLACK_APP_TOKEN"])
    await handler.start_async()


async def start():
    logger.info("Starting Slack app!!")
    if Config["APP_ENV"] == "production":
        await app.start(port=int(Config["PORT"]))
    if Config["APP_ENV"] == "development":
        await devstart()
