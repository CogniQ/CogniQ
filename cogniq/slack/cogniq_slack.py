from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)


from fastapi import FastAPI, Request, Response
import uvicorn

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import asyncio

from slack_bolt.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_sdk.errors import SlackApiError

from databases import Database
import sqlalchemy

from .history.openai_history import OpenAIHistory
from .history.anthropic_history import AnthropicHistory
from .search import Search
from .state_store import StateStore
from .installation_store import InstallationStore
from .errors import BotTokenNoneError, BotTokenRevokedError, TokenRevokedError


class CogniqSlack:
    def __init__(self, *, config: Dict[str, str]):
        """
        Slack bot with given configuration, app, and logger.

        Parameters:
        config (dict): Configuration for the Slack app with the following keys:
            SLACK_SIGNING_SECRET (str): Slack signing secret.
            HOST (str, default='0.0.0.0'): Host on which the app will be started.
            PORT (str or int, default=3000): Port on which the app will be started.
            APP_ENV (str, either 'production' or 'development'): Environment in which the app is running.

        """

        self.config = config

        self.database_url = config["DATABASE_URL"]

        self.installation_store = InstallationStore(
            client_id=config["SLACK_CLIENT_ID"],
            client_secret=config["SLACK_CLIENT_SECRET"],
            database_url=self.database_url,
            install_path=f"{config['APP_URL']}/slack/install",
        )
        self.state_store = StateStore(
            expiration_seconds=120,
            database_url=self.database_url,
            logger=logger,
        )
        oauth_settings = AsyncOAuthSettings(
            client_id=self.config["SLACK_CLIENT_ID"],
            client_secret=self.config["SLACK_CLIENT_SECRET"],
            scopes=[
                "app_mentions:read",
                "channels:history",
                "chat:write",
                "groups:history",
                "im:history",
                "mpim:history",
            ],
            user_scopes=["search:read"],
            installation_store=self.installation_store,
            user_token_resolution="actor",
            state_store=self.state_store,
            logger=logger,
        )

        app_logger = logging.getLogger(f"{__name__}.slack_bolt")
        app_logger.setLevel(self.config["MUTED_LOG_LEVEL"])
        self.app = AsyncApp(
            logger=app_logger,
            signing_secret=self.config["SLACK_SIGNING_SECRET"],
            installation_store=self.installation_store,
            oauth_settings=oauth_settings,
        )

        # Per https://github.com/slackapi/bolt-python/releases/tag/v1.5.0
        self.app.enable_token_revocation_listeners()

        self.app_handler = AsyncSlackRequestHandler(self.app)
        self.api = FastAPI()

        self.anthropic_history = AnthropicHistory(app=self.app)
        self.openai_history = OpenAIHistory(app=self.app)

        # Set defaults
        self.config.setdefault("HOST", "0.0.0.0")
        self.config.setdefault("PORT", 3000)
        self.config.setdefault("APP_ENV", "production")
        self.search = Search(cslack=self)

    async def initialize_db(self):
        """
        This method initializes the database.
        TODO: This should be moved to a migrations task.
        """
        try:
            async with Database(self.database_url) as database:
                await database.fetch_one("select count(*) from slack_installations")
        except Exception as e:
            engine = sqlalchemy.create_engine(self.database_url)
            self.installation_store.metadata.create_all(engine)
            self.state_store.metadata.create_all(engine)

    async def start(self):
        """
        This method starts the app.

        It performs the following steps:
        1. Initializes an instance of `AsyncApp` with the Slack bot token, signing secret, and logger.
        2. Creates a `History` object for tracking app events and logging history.
        3. Sets up event registrations for the Slack app by calling the registered functions with the `app` instance.
        4. Logs a message indicating that the Slack app is starting.
        5. If the app environment is set to 'production', the app starts listening on the specified port.
           It awaits the `app.start()` method to start the app server.
        6. If the app environment is set to 'development', the app starts listening on the specified port.
           It will reload the app server if any changes are made to the app code.

        Note:
        - The app will keep running until it is manually stopped or encounters an error.
        """
        logger.info("Starting Slack app!!")
        await self.initialize_db()

        @self.api.post("/slack/events")
        async def slack_events(request: Request):
            return await self.app_handler.handle(request)

        @self.api.get("/slack/install")
        async def slack_install(request: Request):
            return await self.app_handler.handle(request)

        @self.api.get("/slack/oauth_redirect")
        async def slack_oauth_redirect(request: Request):
            return await self.app_handler.handle(request)

        reload = self.config["APP_ENV"] == "development"
        # Run the FastAPI app using Uvicorn
        uvicorn_config = uvicorn.Config(
            self.api,
            host=self.config["HOST"],
            port=int(self.config["PORT"]),
            log_level=self.config["LOG_LEVEL"],
            reload=reload,
        )
        uvicorn_server = uvicorn.Server(uvicorn_config)
        await uvicorn_server.serve()

    async def chat_update(
        self, *, channel: str, ts: float, context: Dict, text: str, retry_on_rate_limit: bool = True, retry_on_revoked_token: bool = True
    ):
        """
        Updates the chat message in the given channel and thread with the given text.
        """
        bot_token = context.get("bot_token")
        if bot_token is None:
            logger.debug("bot_token is not set. Context: %s", context)
            raise BotTokenNoneError(context=context)
        try:
            await self.app.client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
                token=bot_token,
            )
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                if retry_on_rate_limit:
                    # Extract the retry value from the headers
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    # Wait for the requested amount of time before retrying
                    await asyncio.sleep(retry_after)
                    await self.chat_update(
                        channel=channel,
                        ts=ts,
                        text=text,
                        context=context,
                        retry_on_rate_limit=retry_on_rate_limit,
                    )
                else:
                    # Log the rate limit error and move on
                    logger.error("Rate limit hit, not retrying: %s", e)
            if e.response["error"] == "invalid_refresh_token":
                logger.error("Invalid refresh token, not retrying: %s", e)
                raise TokenRevokedError(message="Invalid refresh token", context=context)
            if e.response["error"] == "token_revoked":
                if retry_on_revoked_token:
                    logger.warn("I must have tried to use a revoked token. I'll try to fetch a newer one.")
                    bot_token = await self.installation_store.async_find_bot_token(context=context)
                    new_context = context.copy()
                    new_context["bot_token"] = bot_token
                    await self.chat_update(
                        channel=channel,
                        ts=ts,
                        text=text,
                        context=new_context,
                        retry_on_rate_limit=retry_on_rate_limit,
                        retry_on_revoked_token=False,  # Try once, but don't retry again
                    )
                else:
                    raise BotTokenRevokedError(message=e, context=context)
            else:
                raise e
