import logging
import os

from cogniq.slack import CogniqSlack

from haystack.nodes.prompt.invocation_layer import AnthropicClaudeInvocationLayer


class Ask:
    def __init__(
        self, *, config: dict, logger: logging.Logger, cslack: CogniqSlack, **kwargs
    ):
        """
        Ask subclass of ChatAnthropic personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, logger=logger, cslack=cslack)
        await ask.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat Anthropic personality with the following keys:
            ANTHROPIC_API_KEY (str): Anthropics API key.

        logger (logging.Logger): Logger to log information about the app's status.
        cslack (CogniqSlack): CogniqSlack instance.

        """
        self.logger = logger
        self.config = config
        self.cslack = cslack

    async def async_setup(self):
        """
        Call me after initializing this class!
        """
        self.bot_id = await self.cslack.anthropic_history.get_bot_user_id()
        self.bot_name = await self.cslack.anthropic_history.get_bot_name()

    async def ask(self, *, q, message_history=""):
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

        self.logger.info(f"res: {res}")
        return "".join(res)
