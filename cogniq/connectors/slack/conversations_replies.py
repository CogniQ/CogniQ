# conversations_replies.py
from slack_sdk.errors import SlackApiError
from cogniq.logging import setup_logger

logger = setup_logger(__name__)


async def fetch_conversations_replies(client, channel_id, thread_ts):
    try:
        replies_response = await client.conversations_replies(
            channel=channel_id, ts=thread_ts
        )
        return replies_response
    except SlackApiError as e:
        logger.error(f"Error fetching conversation replies: {e}")
        return None
