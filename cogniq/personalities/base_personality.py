import abc

from cogniq.slack import CogniqSlack


class BasePersonality(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, cslack: CogniqSlack, **kwargs):
        pass

    @abc.abstractmethod
    def ask_task(self, *, event, reply_ts, **kwargs):
        pass

    @property
    @abc.abstractmethod
    def wake_pattern(self):
        pass
