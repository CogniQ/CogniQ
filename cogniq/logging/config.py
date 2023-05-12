import os
import logging

Config = {
    "APP_ENV": os.environ.get("APP_ENV", "production"),
}

Config["LOG_LEVEL"] = (
    logging.DEBUG if Config["APP_ENV"] == "development" else logging.WARNING
)
Config["MUTED_LOG_LEVEL"] = (
    logging.WARNING if Config["APP_ENV"] == "development" else logging.INFO
)
