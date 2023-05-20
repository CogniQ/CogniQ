import os


config = {
    "SLACK_BOT_TOKEN": os.environ.get("SEARCH_SLACK_BOT_TOKEN"),
    "SLACK_SIGNING_SECRET": os.environ.get("SEARCH_SLACK_SIGNING_SECRET"),
    "SLACK_APP_TOKEN": os.environ.get("SEARCH_SLACK_APP_TOKEN"),
    "HOST": os.environ.get("SEARCH_HOST") or "0.0.0.0",
    "PORT": os.environ.get("SEARCH_PORT") or "3000",
    "APP_ENV": os.environ.get("APP_ENV") or "production",
    "BING_SUBSCRIPTION_KEY": os.environ["BING_SUBSCRIPTION_KEY"],
    "BING_SEARCH_ENDPOINT": os.environ.get(
        "BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com"
    ),
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
}
