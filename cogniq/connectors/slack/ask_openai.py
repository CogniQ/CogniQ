from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.models.openai import ask


async def ask_openai(*, event, say, app, history):
    original_ts = event["ts"]
    channel = event["channel"]
    message = event["text"]
    reply = await say(
        f"Hey <@{event['user']}>, let me figure that out...", thread_ts=original_ts
    )
    reply_ts = reply["ts"]
    openai_response = await ask(q=message, message_history=history)
    # logger.debug(openai_response)
    await app.client.chat_update(channel=channel, ts=reply_ts, text=openai_response)
