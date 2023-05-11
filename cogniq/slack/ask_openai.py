import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor as PoolExecutor
import asyncio
from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.openai import ask

executor = PoolExecutor(mp_context=mp.get_context('fork'), max_workers=10) # https://stackoverflow.com/questions/64501481/python-concurrent-futures-processpoolexecutor-and-global-variables-works-on-lin

async def ask_openai_task(*, event, reply_ts, app, history):
    channel = event["channel"]
    message = event["text"]
    bot_id = event.get("bot_id")
    openai_response = await ask(q=message, message_history=history, bot_id=bot_id)
    # logger.debug(openai_response)
    await app.client.chat_update(channel=channel, ts=reply_ts, text=openai_response)

def run_in_new_loop(coroutine):
    new_loop = asyncio.new_event_loop()
    try:
        return new_loop.run_until_complete(coroutine)
    finally:
        new_loop.close()

def ask_openai(*, event, reply_ts, app, history):
    executor.submit(run_in_new_loop, ask_openai_task(event=event, reply_ts=reply_ts, app=app, history=history))
