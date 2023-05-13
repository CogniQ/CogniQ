import cogniq
import asyncio
from cogniq.logging import setup_logger

logger = setup_logger(__name__)

async def async_main():
    loop = asyncio.get_event_loop()    
    try:
        task = loop.create_task(cogniq.slack.start())
    except KeyboardInterrupt:
        try: 
            for task in asyncio.all_tasks(loop):
                task.cancel()  
            group = asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True)
            loop.run_until_complete(group)  
        except Exception as e:
            logger.exception('Error occurred cancelling tasks')
    finally:
        loop.close()

if __name__ == "__main__":
    asyncio.run(async_main())