import abc

from cogniq.slack import CogniqSlack


class BasePersonality(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, cslack: CogniqSlack, **kwargs):
        pass

    @abc.abstractmethod
    def ask_task(self, *, event, reply_ts, **kwargs):
        pass

    @abc.abstractmethod
    def async_setup(self):
        pass

    @abc.abstractmethod
    def ask_directly(self, *, q, message_history, **kwargs):
        pass

    @property
    @abc.abstractmethod
    def description(self):
        pass