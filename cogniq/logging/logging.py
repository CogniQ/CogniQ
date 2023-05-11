import logging
import os

from .config import Config

# Set default logging level as well
logging.basicConfig(level=Config["MUTED_LOG_LEVEL"])


def do_setup_logger(name, log_level):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
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


def setup_logger(name):
    return do_setup_logger(name, Config["LOG_LEVEL"])


def setup_muted_logger(name):
    return do_setup_logger(name, Config["MUTED_LOG_LEVEL"])
