import logging

logger = logging.getLogger(__name__)
from slack_bolt.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from fastapi import FastAPI, Request, Response
import uvicorn

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import asyncio

from .history.openai_history import OpenAIHistory
from .history.anthropic_history import AnthropicHistory


class CogniqSlack:
    def __init__(self, *, config: dict):
        """
        Slack bot with given configuration, app, and logger.

        Parameters:
        config (dict): Configuration for the Slack app with the following keys:
            SLACK_BOT_TOKEN (str): Slack bot token.
            SLACK_SIGNING_SECRET (str): Slack signing secret.
            HOST (str, default='0.0.0.0'): Host on which the app will be started.
            PORT (str or int, default=3000): Port on which the app will be started.
            APP_ENV (str, either 'production' or 'development'): Environment in which the app is running.
            SLACK_APP_TOKEN (str, optional): Slack app token. Required if APP_ENV is 'development'.
            HISTORY_CLASS (class, optional): Class to use for storing and retrieving history formatted for LLM consumption. Defaults to OpenAIHistory.


        """

        self.config = config

        self.app = AsyncApp(
            token=self.config["SLACK_BOT_TOKEN"],
            signing_secret=self.config["SLACK_SIGNING_SECRET"],
        )

        self.app_handler = AsyncSlackRequestHandler(self.app)
        self.api = FastAPI()

        self.anthropic_history = AnthropicHistory(app=self.app)
        self.openai_history = OpenAIHistory(app=self.app)

        # Set defaults
        self.config.setdefault("HOST", "0.0.0.0")
        self.config.setdefault("PORT", 3000)
        self.config.setdefault("APP_ENV", "production")
        self.config.setdefault("HISTORY_CLASS", OpenAIHistory)

        if self.config["APP_ENV"] == "development" and not self.config.get(
            "SLACK_APP_TOKEN"
        ):
            raise ValueError("SLACK_APP_TOKEN is required in development mode")

        self.history = self.config["HISTORY_CLASS"](app=self.app)

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
        6. If the app environment is set to 'development', it starts the app using the Socket Mode Handler.
           It creates an instance of `AsyncSocketModeHandler` with the `app` instance and the Slack app token.
           It awaits the `handler.start_async()` method to start the app in development mode.

        Note:
        - If the app environment is 'development', make sure to provide the `SLACK_APP_TOKEN` in the configuration.
        - The app will keep running until it is manually stopped or encounters an error.
        """
        logger.info("Starting Slack app!!")
        if self.config["APP_ENV"] == "production":

            @self.api.post("/slack/events")
            async def slack_events(request: Request):
                return await self.app_handler.handle(request)

            # Run the FastAPI app using Uvicorn
            uvicorn_config = uvicorn.Config(
                self.api,
                host=self.config["HOST"],
                port=int(self.config["PORT"]),
                log_level=self.config["LOG_LEVEL"],
            )
            uvicorn_server = uvicorn.Server(uvicorn_config)
            await uvicorn_server.serve()

        if self.config["APP_ENV"] == "development":
            from slack_bolt.adapter.socket_mode.aiohttp import (
                AsyncSocketModeHandler,
            )

            handler = AsyncSocketModeHandler(self.app, self.config["SLACK_APP_TOKEN"])
            await handler.start_async()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=2, min=2, max=8),
        retry=retry_if_exception_type(asyncio.TimeoutError),
    )
    async def chat_update(self, *, channel, ts, text):
        """
        Updates the chat message in the given channel and thread with the given text.
        """
        await self.app.client.chat_update(
            channel=channel,
            ts=ts,
            text=text,
        )
