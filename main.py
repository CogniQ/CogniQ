import logging

import asyncio

from config import config
from multiple_personalities import MultiplePersonalities


def setup_root_logger(level=logging.DEBUG):
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root.addHandler(handler)


if __name__ == "__main__":
    setup_root_logger(level=config["MUTED_LOG_LEVEL"])

    mp = MultiplePersonalities(config=config)
    asyncio.run(mp.start())
