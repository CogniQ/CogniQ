import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(".env")


# Function to shorten os.getenv calls
def env(var_name, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise EnvironmentError(f"Please supply the {var_name} environment variable.")
    return value


# Required configurations
SLACK_SIGNING_SECRET = env("SLACK_SIGNING_SECRET")
SLACK_CLIENT_ID = env("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = env("SLACK_CLIENT_SECRET")
OPENAI_API_KEY = env("OPENAI_API_KEY")
BING_SUBSCRIPTION_KEY = env("BING_SUBSCRIPTION_KEY")
APP_URL = env("APP_URL")

# Default configurations
HOST = env("HOST", "0.0.0.0")
PORT = env("PORT", "3000")
APP_ENV = env("APP_ENV", "production")
BING_SEARCH_ENDPOINT = env("BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com")

OPENAI_CHAT_MODEL = env("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
OPENAI_MAX_TOKENS_HISTORY = env("OPENAI_MAX_TOKENS_HISTORY", 800)
OPENAI_MAX_TOKENS_RETRIEVAL = env("OPENAI_MAX_TOKENS_RETRIEVAL", 700)
OPENAI_MAX_TOKENS_PROMPT = env("OPENAI_MAX_TOKENS_PROMPT", 1000)
OPENAI_MAX_TOKENS_RESPONSE = env("OPENAI_MAX_TOKENS_RESPONSE", 800)
OPENAI_TOTAL_MAX_TOKENS = env("OPENAI_TOTAL_MAX_TOKENS", 4097)

POSTGRES_HOST = env("POSTGRES_HOST", "localhost")
POSTGRES_USER = env("POSTGRES_USER", "cogniq")
POSTGRES_PASSWORD = env("POSTGRES_PASSWORD", "cogniq")
POSTGRES_DB = env("POSTGRES_DB", "cogniq")

DATABASE_URL = env("DATABASE_URL", f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}")
LOG_LEVEL = logging.DEBUG if APP_ENV == "development" else logging.INFO
MUTED_LOG_LEVEL = logging.WARN if APP_ENV == "development" else logging.WARN
