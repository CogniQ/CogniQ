import abc

from cogniq.slack import CogniqSlack


class BasePersonality(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, cslack: CogniqSlack, **kwargs):
        pass

    @abc.abstractmethod
    async def async_setup(self):
        """
        This will be called after initializing the program.
        """
        pass

    @abc.abstractmethod
    def ask_task(self, *, event, reply_ts, **kwargs):
        """
        This will be called when the wake pattern is matched.
        """
        pass

    @property
    @abc.abstractmethod
    def wake_pattern(self):
        """
        A Regex pattern that will be used to match the wake word.

        In the future, this may be changed to become a callable that returns a boolean.
        """
        pass
