import os

# The default config when a custom config is not supplied.
Config = {
    "SLACK_BOT_TOKEN": os.environ.get("SLACK_BOT_TOKEN"),
    "SLACK_SIGNING_SECRET": os.environ.get("SLACK_SIGNING_SECRET"),
    "HOST": os.environ.get("HOST") or "0.0.0.0",
    "PORT": os.environ.get("PORT") or "3000",
    "APP_ENV": os.environ.get("APP_ENV") or "production",
    "SLACK_APP_TOKEN": os.environ.get("SLACK_APP_TOKEN"),
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
}
