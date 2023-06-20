import logging

logger = logging.getLogger(__name__)

from cogniq.slack import CogniqSlack

from haystack.nodes.prompt.invocation_layer import AnthropicClaudeInvocationLayer


class Ask:
    def __init__(self, *, config: Dict, cslack: CogniqSlack, **kwargs):
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

    async def async_setup(self):
        """
        Call me after initializing this class!
        """
        pass

    async def ask(self, *, q, message_history=None):
        message_history = message_history or ""
        kwargs = {
            "model": "claude-instant-v1-100k",
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
        return "".join(res)
