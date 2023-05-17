import cogniq
import asyncio
from cogniq.logging import setup_logger

logger = setup_logger(__name__)


async def async_main():
    await cogniq.bing_search.start()


if __name__ == "__main__":
    asyncio.run(async_main())
