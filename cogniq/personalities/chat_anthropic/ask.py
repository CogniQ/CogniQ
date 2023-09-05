from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from cogniq.config import ANTHROPIC_API_KEY
from cogniq.personalities import BaseAsk
from cogniq.slack import CogniqSlack

from haystack.nodes.prompt.invocation_layer import AnthropicClaudeInvocationLayer


class Ask(BaseAsk):
    def __init__(self, *, cslack: CogniqSlack, **kwargs):
        """
        Ask subclass of ChatAnthropic personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(cslack=cslack)
        await ask.async_setup()
        ```

        Parameters:
        cslack (CogniqSlack): CogniqSlack instance.

        """

        self.cslack = cslack

    async def async_setup(self) -> None:
        """
        Call me after initializing this class!
        """
        pass

    async def ask(self, *, q: str, message_history: str | None = None) -> Dict[str, Any]:
        message_history = message_history or ""
        kwargs = {
            "model": "claude-2",
            "max_tokens_to_sample": 100000,
            "temperature": 1,
            "top_p": -1,  # disabled
            "top_k": -1,
            "stop_sequences": ["\n\nHuman: "],
            "stream": False,
        }

        api_key = ANTHROPIC_API_KEY
        layer = AnthropicClaudeInvocationLayer(api_key=api_key, **kwargs)
        newprompt = f"{message_history}\n\nHuman: {q}"
        res = layer.invoke(prompt=newprompt)

        logger.info(f"res: {res}")
        answer = "".join(res)
        return {"answer": answer, "response": res}
