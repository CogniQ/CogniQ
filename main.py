from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.personalities import (
    bing_search,
    chat_gpt4,
    chat_anthropic,
)

import asyncio
import os

from cogniq.slack import CogniqSlack
from config import config
from multiple_personalities import (
    register_app_mention,
    register_message,
)


async def multiple_personalities():
    """
    Starts one Slack bot instance, and routes messages according to wake word.
    """
    await CogniqSlack(
        config=config,
        logger=logger,
        register_functions=[register_app_mention, register_message],
    ).start()


if __name__ == "__main__":
    asyncio.run(multiple_personalities())
