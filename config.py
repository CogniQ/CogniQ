import os
import logging
from dotenv import dotenv_values

user_must_supply_these = {
    "SLACK_SIGNING_SECRET": None,
    "SLACK_CLIENT_ID": None,
    "SLACK_CLIENT_SECRET": None,
    "OPENAI_API_KEY": None,
    "BING_SUBSCRIPTION_KEY": None,
    "APP_URL": None,
    "DATABASE_URL": None,
}

# Attempt to load .env values, fallback to empty dict if .env file doesn't exist
try:
    dotenv_config = dotenv_values(".env")
except FileNotFoundError:
    dotenv_config = {}


# Check if user has supplied all required environment variables
for var, default in user_must_supply_these.items():
    if var not in os.environ and var not in dotenv_config:
        raise EnvironmentError(
            f"Please supply the {var} environment variable in your .env file or as an environment variable."
        )

# Merge .env values and environment variables
config = {**dotenv_config, **os.environ}


# Define default values
defaults = {
    "HOST": "0.0.0.0",
    "PORT": "3000",
    "APP_ENV": "production",
    "BING_SEARCH_ENDPOINT": "https://api.bing.microsoft.com",
    "OPENAI_CHAT_MODEL": "gpt-3.5-turbo",
    "OPENAI_MAX_TOKENS_HISTORY": 800,
    "OPENAI_MAX_TOKENS_RETRIEVAL": 700,
    "OPENAI_MAX_TOKENS_PROMPT": 1000,
    "OPENAI_MAX_TOKENS_RESPONSE": 800,
    "OPENAI_TOTAL_MAX_TOKENS": 4097,
}
for var, default in defaults.items():
    config.setdefault(var, default)


# Set logging level
config["LOG_LEVEL"] = logging.DEBUG if config["APP_ENV"] == "development" else logging.INFO
config["MUTED_LOG_LEVEL"] = logging.WARN if config["APP_ENV"] == "development" else logging.WARN
