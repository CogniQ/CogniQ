import os
import logging

Config = {
    "APP_ENV": os.environ.get(
        "APP_ENV", "production"
    ),
}

Config["LOG_LEVEL"] = logging.WARNING if Config["APP_ENV"] == "development" else logging.INFO
Config["MUTED_LOG_LEVEL"] = logging.INFO if Config["APP_ENV"] == "development" else logging.ERROR