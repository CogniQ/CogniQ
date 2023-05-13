import asyncio
import sys

from signal import signal, SIGINT

def signal_handler(signal, frame):
    loop = asyncio.get_event_loop()
    loop.stop()
    for task in asyncio.all_tasks(loop):
        task.cancel()
    group = asyncio.gather(*asyncio.all_tasks(loop), loop=loop, return_exceptions=True)
    loop.run_until_complete(group)
    print('Event loop closed.')
    sys.exit(0)

signal(SIGINT, signal_handler)