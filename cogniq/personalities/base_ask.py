from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import abc

from cogniq.slack import CogniqSlack

from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack


class BaseAsk(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(
        self,
        *,
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
        **kwargs,
    ):
        """
        Ask subclass of the X personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(cslack=cslack, copenai=copenai)
        await ask.async_setup()
        ```

        Parameters:
        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.

        """

        pass

    @abc.abstractmethod
    async def async_setup(self) -> None:
        """
        Call me after initialization, please!
        """
        pass

    @abc.abstractmethod
    async def ask(
        self,
        *,
        q,
        message_history: List[dict[str, str]],
        personalities: Dict,
        context: Dict,
        stream_callback: Callable[..., None] | None = None,
    ) -> Dict[str, Any]:
        """
        Ask a question to the personality.
        """
        pass
