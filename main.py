import logging

import asyncio

from config import config
from multiple_personalities import MultiplePersonalities


def setup_root_logger(level=logging.INFO):
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root.addHandler(handler)


def mute_certain_loggers(level=logging.WARN):
    logs = [
        "generalimport.general_importer",
        "aiosqlite",
        "databases",
        "slack_sdk.web.async_base_client",
        "haystack.telemetry",
        "haystack.utils.openai_utils",
        "asyncio",
    ]
    for logger_name in logs:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)


if __name__ == "__main__":
    setup_root_logger(level=config["LOG_LEVEL"])
    mute_certain_loggers(level=config["MUTED_LOG_LEVEL"])

    mp = MultiplePersonalities(config=config)
    asyncio.run(mp.start())
