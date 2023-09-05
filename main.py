from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import asyncio
from cogniq.config import LOG_LEVEL, MUTED_LOG_LEVEL
from multiple_personalities import MultiplePersonalities


def setup_root_logger(level: int):
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root.addHandler(handler)


def mute_certain_loggers(level: int):
    logs = [
        "generalimport",
        "aiosqlite",
        "databases",
        "slack_sdk",
        "haystack",
        "asyncio",
        "sseclient",
        "urllib3",
    ]
    for log in logs:
        logging.getLogger(log).setLevel(level)
    for logger_name in logging.root.manager.loggerDict.keys():
        for log in logs:
            if logger_name.startswith(log):
                logger = logging.getLogger(logger_name)
                logger.setLevel(level)
                break


if __name__ == "__main__":
    setup_root_logger(level=LOG_LEVEL)
    mute_certain_loggers(level=MUTED_LOG_LEVEL)

    mp = MultiplePersonalities()

    asyncio.run(mp.start())
