from typing import *

import logging

logger = logging.getLogger(__name__)


class TokenNoneError(Exception):
    """Raised when the either a bot or user token is None."""

    def __init__(self, message: str = "Token is None.", context: Dict[str, Any] | None = None) -> None:
        self.context = context
        super().__init__(message)

    def log_debug(self) -> None:
        pass
        # logger.debug(f"#{self.__class__} context: {self.context}") # Leave commented by default as context includes tokens and should only be enabled strictly when necessary.


class UserTokenNoneError(TokenNoneError):
    """Raised when the user token is None."""

    def __init__(self, message: str = "User token is None", context: Dict[str, Any] | None = None) -> None:
        super().__init__(message, context)


class BotTokenNoneError(TokenNoneError):
    """Raised when the bot token is None."""

    def __init__(self, message: str = "Bot token is None", context: Dict[str, Any] | None = None) -> None:
        super().__init__(message, context)


class TokenRevokedError(TokenNoneError):
    """Raised when the either a bot or user token is revoked."""

    def __init__(self, message: str = "Token is Revoked.", context: Dict[str, Any] | None = None) -> None:
        super().__init__(message, context)


class UserTokenRevokedError(TokenRevokedError):
    """Raised when the user token is revoked."""

    def __init__(self, message: str = "User Token is Revoked.", context: Dict[str, Any] | None = None) -> None:
        super().__init__(message, context)


class BotTokenRevokedError(TokenRevokedError):
    """Raised when the bot token is revoked."""

    def __init__(self, message: str = "Bot Token is Revoked.", context: Dict[str, Any] | None = None) -> None:
        super().__init__(message, context)


class RefreshTokenInvalidError(TokenNoneError):
    """Raised when the either a bot or user refresh token is invalid."""

    def __init__(self, message: str = "Refresh Token is Invalid.", context: Dict[str, Any] | None = None) -> None:
        super().__init__(message, context)