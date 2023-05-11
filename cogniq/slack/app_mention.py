from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .history import fetch_history
from .ask_openai import ask_openai


def register_app_mention(*, app):
    @app.event("app_mention")
    async def query_openai(event, say):
        original_ts = event["ts"]
        reply = await say(
            f"Hey <@{event['user']}>, let me figure that out...", thread_ts=original_ts
        )
        reply_ts = reply["ts"]
        history = await fetch_history(app=app, event=event)
        # logger.debug(f"history: {history}")
        ask_openai(event=event, reply_ts=reply_ts, app=app, history=history)
