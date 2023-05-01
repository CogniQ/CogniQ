from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from slack_sdk.errors import SlackApiError
from .conversations_replies import fetch_conversations_replies


def filter_message(message):
    return {
        "timestamp": message.get("ts"),
        "user": message.get("user"),
        "text": message.get("text"),
        "thread_ts": message.get("thread_ts"),
    }


async def fetch_conversations_history(client, channel_id):
    messages = []
    cursor = None

    try:
        while True:
            response = await client.conversations_history(
                channel=channel_id, cursor=cursor
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
                logger.debug(f"appending to history: {filtered_message}")
                messages.append(filtered_message)

            if response["has_more"]:
                break  # Limit historical lookup. We don't want to abuse our rate limit. TODO: After we implement persistent data storage, implement caching.
                cursor = response["response_metadata"]["next_cursor"]
            else:
                break

        return messages
    except SlackApiError as e:
        logger.error(f"Error fetching conversation history: {e}")
        return None
