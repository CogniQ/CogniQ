from slack_sdk.errors import SlackApiError
from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.openai import user_message, system_message, assistant_message
from .conversations_history import fetch_conversations_history
from .conversations_replies import fetch_conversations_replies


async def get_bot_user_id(app):
    auth_test = await app.client.auth_test()
    return auth_test["user_id"]


async def fetch_history(app, event):
    channel_id = event["channel"]
    thread_ts = event.get("thread_ts")
    response = None
    if thread_ts is None:
        response = await fetch_conversations_history_and_convert_to_openai_sequence(
            app=app, channel_id=channel_id
        )
    else:
        response = await fetch_conversations_replies_and_convert_to_openai_sequence(
            app=app, channel_id=channel_id, thread_ts=thread_ts
        )
    logger.debug(f"History: {response}")
    return response


def convert_to_openai_sequence(*, messages, bot_user_id):
    openai_sequence = []
    for message in messages:
        if message.get("user") == bot_user_id:
            openai_sequence.append(assistant_message(message.get("text")))
        else:
            openai_sequence.append(user_message(message.get("text")))
        if message.get("replies"):
            for reply in message.get("replies"):
                if reply.get("user") == bot_user_id:
                    openai_sequence.append(assistant_message(reply.get("text")))
                else:
                    openai_sequence.append(user_message(reply.get("text")))
    return openai_sequence


async def fetch_conversations_history_and_convert_to_openai_sequence(
    *, app, channel_id
):
    """The most recent messages in the time range are returned first."""
    messages = await fetch_conversations_history(app.client, channel_id)
    if messages is None:
        return None
    bot_user_id = await get_bot_user_id(app)
    return convert_to_openai_sequence(
        messages=reversed(messages), bot_user_id=bot_user_id
    )


async def fetch_conversations_replies_and_convert_to_openai_sequence(
    *, app, channel_id, thread_ts
):
    """The earliest messages in the time range are returned first."""

    messages = await fetch_conversations_replies(app.client, channel_id, thread_ts)
    if messages is None:
        return None
    bot_user_id = await get_bot_user_id(app)
    return convert_to_openai_sequence(messages=messages, bot_user_id=bot_user_id)
