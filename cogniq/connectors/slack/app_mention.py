from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .history import fetch_history
from .ask_openai import ask_openai


def register_app_mention(*, app):
    @app.event("app_mention")
    async def query_openai(event, say):
        channel = event["channel"]
        history = await fetch_history(client=app.client, event=event)
        logger.debug(f"history: {history}")
        await ask_openai(event=event, say=say, app=app, history=history)
