from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from wandb.sdk.data_types.trace_tree import Trace
from haystack.nodes.prompt.invocation_layer import AnthropicClaudeInvocationLayer


from cogniq.personalities import BaseAsk
from cogniq.slack import CogniqSlack
from cogniq.wandb import WandbChildSpan


class Ask(BaseAsk):
    def __init__(self, *, config: Dict[str, str], cslack: CogniqSlack, **kwargs):
        """
        Ask subclass of ChatAnthropic personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, cslack=cslack)
        await ask.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat Anthropic personality with the following keys:
            ANTHROPIC_API_KEY (str): Anthropics API key.


        cslack (CogniqSlack): CogniqSlack instance.

        """

        self.config = config
        self.cslack = cslack

    async def async_setup(self) -> None:
        """
        Call me after initializing this class!
        """
        pass

    async def ask(self, *, q: str, message_history: str | None = None, parent_span: Trace) -> Dict[str, Any]:
        with WandbChildSpan(parent_span=parent_span, name="bing_search", kind="agent") as span:
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

            api_key = self.config["ANTHROPIC_API_KEY"]
            layer = AnthropicClaudeInvocationLayer(api_key=api_key, **kwargs)
            newprompt = f"{message_history}\n\nHuman: {q}"
            res = layer.invoke(prompt=newprompt)

            logger.info(f"res: {res}")
            answer = "".join(res)
            span.add_inputs_and_outputs(inputs={"query": q}, outputs={"answer": answer})
            return {"answer": answer, "response": res}
