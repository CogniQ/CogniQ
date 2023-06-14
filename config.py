import os
import logging
from dotenv import dotenv_values

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
}

# Attempt to load .env values, fallback to empty dict if .env file doesn't exist
try:
    dotenv_config = dotenv_values(".env")
except FileNotFoundError:
    dotenv_config = {}

# Merge .env values and environment variables
config = {**dotenv_config, **os.environ}

# Set default values if neither an environment variable nor a .env value is present
for var, default in defaults.items():
    config.setdefault(var, default)

config["LOG_LEVEL"] = logging.DEBUG if config["APP_ENV"] == "development" else logging.INFO
config["MUTED_LOG_LEVEL"] = logging.INFO if config["APP_ENV"] == "development" else logging.INFO
