import abc

from cogniq.slack import CogniqSlack


class BasePersonality(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, cslack: CogniqSlack, **kwargs):
        pass

    @abc.abstractmethod
    def ask_task(self, *, event, reply_ts, **kwargs):
        """
        Ask a question of the personality and have it reply to the given channel and thread.
        """
        pass

    @abc.abstractmethod
    def async_setup(self):
        """
        Perform any asynchronous setup tasks.
        """
        pass

    @abc.abstractmethod
    def ask_directly(self, *, q, message_history, **kwargs):
        """
        Ask a question of the personality and return the response.
        """
        pass

    @property
    @abc.abstractmethod
    def description(self):
        """
        A short description of the personality. This is used by an evaluator to note the context of the response.
        """
        pass
