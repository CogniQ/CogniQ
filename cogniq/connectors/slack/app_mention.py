from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .conversations_history import fetch_conversations_history
from .ask_openai import ask_openai


def register_app_mention(*, app):
    @app.event("app_mention")
    async def query_openai(event, say):
        await ask_openai(event=event, say=say, app=app)
