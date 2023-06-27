from typing import *


class UserTokenNoneError(Exception):
    """Raised when the user token is None."""

    def __init__(self, context: Dict) -> None:
        self.context = context
        super().__init__(f"User token is None.")


class BotTokenNoneError(Exception):
    """Raised when the bot token is None."""

    def __init__(self, context: Dict) -> None:
        self.context = context
        super().__init__(f"Bot token is None.")
