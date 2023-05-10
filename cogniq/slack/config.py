import os


Config = {
    "SLACK_BOT_TOKEN": os.environ.get("SLACK_BOT_TOKEN"),
    "SLACK_SIGNING_SECRET": os.environ.get("SLACK_SIGNING_SECRET"),
    "PORT": os.environ.get("PORT") or "3000",
    "APP_ENV": os.environ.get("APP_ENV") or "production",
    "SLACK_APP_TOKEN": os.environ.get("SLACK_APP_TOKEN"),
}
