from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from slack_sdk.errors import SlackApiError
from .conversations_replies import fetch_conversations_replies

from cogniq.models.openai import user_message, system_message, assistant_message


def filter_message(message):
    return {
        "timestamp": message.get("ts"),
        "user": message.get("user"),
        "text": message.get("text"),
        "thread_ts": message.get("thread_ts"),
    }


async def get_bot_user_id(client):
    try:
        response = await client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        logger.error(f"Error fetching bot user ID: {e}")
        return None


async def fetch_conversations_history(client, channel_id):
    messages = []
    cursor = None

    try:
        while True:
            response = await client.conversations_history(
                channel=channel_id,
                limit=20,  # TODO: temporary limit. We need to implement vector search.
                cursor=cursor,
            )

            for message in response["messages"]:
                filtered_message = filter_message(message)
                if filtered_message.get("thread_ts") is not None:
                    replies_response = await fetch_conversations_replies(
                        client, channel_id, filtered_message.get("thread_ts")
                    )
                    if replies_response:
                        replies = [
                            filter_message(reply)
                            for reply in replies_response["messages"]
                            if filter_message(reply)
                        ]
                        filtered_message["replies"] = replies
                # logger.debug(f"appending to history: {filtered_message}")
                messages.append(filtered_message)

            if response["has_more"]:
                break  # Limit historical lookup. We don't want to abuse our rate limit. TODO: After we implement persistent data storage, implement caching.
                cursor = response["response_metadata"]["next_cursor"]
            else:
                break

        return messages
    except SlackApiError as e:
        logger.error(f"Error fetching conversation history: {e}")
        raise e


def convert_to_openai_sequence(messages, bot_user_id):
    openai_sequence = []
    for message in reversed(
        messages
    ):  # Slack returns in reverse chronological order (latest to earliest). We want chronological order.
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
    client, channel_id
):
    bot_user_id = await get_bot_user_id(client)
    messages = await fetch_conversations_history(client, channel_id)
    if messages is None:
        return None
    return convert_to_openai_sequence(messages, bot_user_id)
