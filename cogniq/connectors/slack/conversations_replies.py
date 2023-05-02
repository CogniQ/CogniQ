# conversations_replies.py
from slack_sdk.errors import SlackApiError
from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from slack_sdk.errors import SlackApiError


def filter_message(message):
    return {
        "ts": message.get("ts"),
        "user": message.get("user"),
        "text": message.get("text"),
        "thread_ts": message.get("thread_ts"),
    }


async def fetch_conversations_replies(client, channel_id, thread_ts):
    messages = []
    cursor = None

    try:
        while True:
            response = await client.conversations_replies(
                channel=channel_id,
                limit=50,  # TODO: temporary limit. We need to implement vector search.
                ts=thread_ts,
            )

            for message in response["messages"]:
                filtered_message = filter_message(message)
                messages.append(filtered_message)

            if response["has_more"]:
                break  # Limit historical lookup. We don't want to abuse our rate limit. TODO: After we implement persistent data storage, implement caching.
                cursor = response["response_metadata"]["next_cursor"]
            else:
                break
        # logger.debug(f"replies: {messages}")
        return messages
    except SlackApiError as e:
        logger.error(f"Error fetching conversation replies: {e}")
        raise e
