from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.openai import ask

from cogniq.slack import CogniqSlack

async def ask_openai_task(*, event, reply_ts, cslack: CogniqSlack):
    channel = event["channel"]
    message = event["text"]
    bot_id = event.get("bot_id")
    history = await cslack.history.fetch_history(event=event)
    # logger.debug(f"history: {history}")

    openai_response = await ask(q=message, message_history=history, bot_id=bot_id)
    # logger.debug(openai_response)
    await cslack.app.client.chat_update(
        channel=channel, ts=reply_ts, text=openai_response
    )
