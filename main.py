import cogniq
import asyncio
from cogniq.logging import setup_logger

logger = setup_logger(__name__)

async def async_main():
    try:
        await cogniq.slack.start()
    except KeyboardInterrupt:
        try: 
            for task in asyncio.all_tasks():
                task.cancel()  
            await asyncio.gather(*asyncio.all_tasks(), return_exceptions=True)
        except Exception as e:
            logger.exception('Error occurred cancelling tasks')

if __name__ == "__main__":
    asyncio.run(async_main())
