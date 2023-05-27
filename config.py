import os
import logging

config = {
    "SLACK_BOT_TOKEN": os.environ.get("SLACK_BOT_TOKEN"),
    "SLACK_SIGNING_SECRET": os.environ.get("SLACK_SIGNING_SECRET"),
    "SLACK_APP_TOKEN": os.environ.get("SLACK_APP_TOKEN"),
    "HOST": os.environ.get("HOST") or "0.0.0.0",
    "PORT": os.environ.get("PORT") or "3000",
    "APP_ENV": os.environ.get("APP_ENV") or "production",
    "BING_SUBSCRIPTION_KEY": os.environ["BING_SUBSCRIPTION_KEY"],
    "BING_SEARCH_ENDPOINT": os.environ.get(
        "BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com"
    ),
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
    "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
    "OPENAI_API_TYPE": os.environ.get("OPENAI_API_TYPE"),  # Azure
    "OPENAI_API_BASE": os.environ.get("OPENAI_API_BASE"),  # Azure
    "OPENAI_API_VERSION": os.environ.get("OPENAI_API_VERSION"),  # Azure
    "OPENAI_CHAT_MODEL": os.environ.get("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
    "OPENAI_MAX_TOKENS_HISTORY": os.environ.get("OPENAI_MAX_TOKENS_HISTORY", 800),
    "OPENAI_MAX_TOKENS_RETRIEVAL": os.environ.get("OPENAI_MAX_TOKENS_RETRIEVAL", 700),
    "OPENAI_MAX_TOKENS_PROMPT": os.environ.get("OPENAI_MAX_TOKENS_PROMPT", 1000),
    "OPENAI_MAX_TOKENS_RESPONSE": os.environ.get("OPENAI_MAX_TOKENS_RESPONSE", 800),
}

config["LOG_LEVEL"] = (
    logging.DEBUG if config["APP_ENV"] == "development" else logging.INFO
)
config["MUTED_LOG_LEVEL"] = (
    logging.INFO if config["APP_ENV"] == "development" else logging.INFO
)
