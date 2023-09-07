from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import abc
from slack_bolt.async_app import AsyncApp


class BaseHistory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *, app: AsyncApp):
        pass

    @abc.abstractmethod
    async def get_bot_user_id(self, *, context: Dict) -> str:
        pass

    @abc.abstractmethod
    async def get_bot_name(self, *, context: Dict) -> str:
        pass

    @abc.abstractmethod
    async def get_history(self, *, event: Dict, context: Dict) -> List[Dict[str, str]]:
        pass
