from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)


def message(role: str, content: str) -> Dict[str, str]:
    return {"role": f"{role}", "content": f"{content}"}


def user_message(content: str) -> Dict[str, str]:
    return message("user", content)


def system_message(content: str) -> Dict[str, str]:
    return message("system", content)


def assistant_message(content: str) -> Dict[str, str]:
    return message("assistant", content)


def message_to_string(message: Dict[str, str]) -> str:
    return f"{message['role']}: {message['content']}"
