import os

# The default config when a custom config is not supplied.
default_config = {
    "SLACK_BOT_TOKEN": os.environ.get("SLACK_BOT_TOKEN"),
    "SLACK_SIGNING_SECRET": os.environ.get("SLACK_SIGNING_SECRET"),
    "HOST": os.environ.get("HOST") or "0.0.0.0",
    "PORT": os.environ.get("PORT") or "3000",
    "APP_ENV": os.environ.get("APP_ENV") or "production",
    "SLACK_APP_TOKEN": os.environ.get("SLACK_APP_TOKEN"),
    "BING_SUBSCRIPTION_KEY": os.environ["BING_SUBSCRIPTION_KEY"],
    "BING_SEARCH_ENDPOINT": os.environ.get(
        "BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com"
    ),
}
