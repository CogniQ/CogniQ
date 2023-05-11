from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from slack_sdk.errors import SlackApiError
from .history import fetch_history
from .ask_openai import ask_openai


def register_message(*, app):
    @app.event("message")
    async def handle_message_events(event, say):
        channel_type = event["channel_type"]
        user = event["user"]
        if channel_type == "im":
            original_ts = event["ts"]
            reply = await say(
                f"Hey <@{event['user']}>, let me figure that out...", thread_ts=original_ts
            )
            reply_ts = reply["ts"]
            history = await fetch_history(app=app, event=event)
            ask_openai(event=event, reply_ts=reply_ts, app=app, history=history)
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
