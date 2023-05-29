import logging

import abc
from slack_bolt.async_app import AsyncApp


class BaseHistory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *, app: AsyncApp):
        pass

    @abc.abstractmethod
    async def get_bot_user_id(self) -> str:
        pass

    @abc.abstractmethod
    async def get_bot_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_history(self, *, event, **kwargs):
        pass