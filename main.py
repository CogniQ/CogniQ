from cogniq.logging import setup_logger

logger = setup_logger(__name__)

import asyncio

from config import config
from multiple_personalities import MultiplePersonalities


if __name__ == "__main__":
    mp = MultiplePersonalities(config=config, logger=logger)
    asyncio.run(mp.start())
