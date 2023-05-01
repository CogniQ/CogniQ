from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.models.openai import ask
from .conversations_history import fetch_conversations_history_and_convert_to_openai_sequence


async def ask_openai(*, event, say, app):
    original_ts = event["ts"]
    channel = event["channel"]
    message = event["text"]
    reply = await say(
        f"Hey <@{event['user']}>, let me figure that out...", thread_ts=original_ts
    )
    reply_ts = reply["ts"]
    history = await fetch_conversations_history_and_convert_to_openai_sequence(client=app.client, channel_id=channel) # TODO: retrieval is the name of the game. Enhance this with proper search.
    logger.debug(f"history: {history}")
    openai_response = await ask(q=message, message_history=history)
    # logger.debug(openai_response)
    await app.client.chat_update(
        channel=channel,
        ts=reply_ts,
        text=openai_response
    )
