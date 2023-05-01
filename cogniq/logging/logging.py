import logging
import os

def setup_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        app_env = os.getenv("APP_ENV", "production")  # Default to 'production' if APP_ENV is not set
        log_level = logging.DEBUG if app_env == "development" else logging.INFO

        logger.setLevel(log_level)
        logger.propagate = False

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create a formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Add the formatter to the console handler
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        logger.addHandler(console_handler)

    return logger
