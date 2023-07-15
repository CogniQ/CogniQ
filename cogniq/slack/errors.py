from typing import *

class TokenNoneError(Exception):
    """Raised when the either a bot or user token is None."""

    def __init__(self, context: Dict[str, Any]) -> None:
        self.context = context
        super().__init__(f"Token is None.")

class UserTokenNoneError(TokenNoneError):
    """Raised when the user token is None."""

    def __init__(self, context: Dict[str, Any]) -> None:
        self.context = context
        super().__init__(f"User token is None.")


class BotTokenNoneError(TokenNoneError):
    """Raised when the bot token is None."""

    def __init__(self, context: Dict[str, Any]) -> None:
        self.context = context
        super().__init__(f"Bot token is None.")

