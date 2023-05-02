from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from slack_sdk.errors import SlackApiError
from .conversations_replies import fetch_conversations_replies, filter_message


async def fetch_conversations_history(client, channel_id):
    messages = []
    cursor = None

    try:
        while True:
            response = await client.conversations_history(
                channel=channel_id,
                limit=10,  # TODO: temporary limit. We need to implement vector search.
                cursor=cursor,
            )

            for message in response["messages"]:
                filtered_message = filter_message(message)
                if filtered_message.get("thread_ts") is not None:
                    replies_response = await fetch_conversations_replies(
                        client, channel_id, filtered_message.get("thread_ts")
                    )
                    filtered_message["replies"] = replies_response
                # logger.debug(f"history: {messages}")
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
