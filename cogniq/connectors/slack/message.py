from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from slack_sdk.errors import SlackApiError
from .conversations_history import fetch_conversations_history
from .ask_openai import ask_openai


def register_message(*, app):
    @app.event("message")
    async def handle_message_events(event, say):
        original_ts = event["ts"]
        channel_type = event["channel_type"]
        channel = event["channel"]
        team = event["team"]
        user = event["user"]
        if channel_type == "im":
            logger.debug(f"<@{user}> IM: {event['text']}")
            await ask_openai(event=event, say=say, app=app)
        # elif channel_type == "mpim":
        #     await say(f"MPIM received from <@{user}>!", thread_ts=original_ts)
        # elif channel_type == "channel":
        #     await say(
        #         f"Channel message received from <@{user}>!", thread_ts=original_ts
        #     )
        # elif channel_type == "group":
        #     await say(f"Group message received from <@{user}>!", thread_ts=original_ts)
        # else:
        #     logger.error(
        #         f"<@{user}> Unknown channel type: {channel_type}: {event['text']}"
        #     )
