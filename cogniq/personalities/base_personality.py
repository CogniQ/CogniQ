from typing import Awaitable
import abc

from cogniq.slack import CogniqSlack


class BasePersonality(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, cslack: CogniqSlack, **kwargs):
        """
        Initialize the BasePersonality.
        :param cslack: CogniqSlack instance.
        :param kwargs: Additional keyword arguments.
        """
        pass

    @abc.abstractmethod
    async def async_setup(self) -> Awaitable[None]:
        """
        Perform any asynchronous setup tasks that are necessary for the personalityto function properly.
        """
        pass

    @abc.abstractmethod
    async def ask_task(self, *, event: dict, reply_ts: float, context: dict) -> Awaitable[None]:
        """
        Ask a question of the personality and have it reply to the given channel and thread.
        :param event: The event data.
        :param reply_ts: The timestamp for the reply.
        :param context: The context data.
        """
        pass

    @abc.abstractmethod
    async def ask_directly(self, *, q, message_history: list[dict[str, str]], context: dict, reply_ts: float = None, **kwargs) -> Awaitable[None]:
        """
        Ask a question of the personality and return the response.
        :param q: The question to ask.
        :param message_history: The message history.
        :param context: The context data.
        :param reply_ts: The timestamp for the reply. If None, behavior may vary.
        :param kwargs: Additional keyword arguments.
        """
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """
        A short description of the personality. This is used by an evaluator to note the context of the response.
        :return: The description of the personality.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        The name of the personality.
        :return: The name of the personality.
        """
        pass