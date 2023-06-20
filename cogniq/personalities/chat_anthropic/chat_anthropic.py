import logging

logger = logging.getLogger(__name__)


from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack

from .ask import Ask


class ChatAnthropic(BasePersonality):
    def __init__(self, *, config: Dict, cslack: CogniqSlack, **kwargs):
        """
        Chat Anthropic personality
        Please call async_setup after initializing the personality.

        ```
        chat_anthropic = ChatAnthropic(config=config, cslack=cslack)
        await chat_anthropic.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat Anthropic personality with the following keys:



        cslack (CogniqSlack): CogniqSlack instance.
        """

        self.config = config
        self.cslack = cslack

        self.ask = Ask(config=config, cslack=cslack)

    async def async_setup(self):
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event: Dict, reply_ts: float, context: Dict):
        channel = event["channel"]
        message = event["text"]

        history = await self.cslack.anthropic_history.get_history(event=event)
        logger.debug(f"history: {history}")

        response = await self.ask.ask(q=message, message_history=history)
        await self.cslack.chat_update(channel=channel, ts=reply_ts, context=context, text=response)

    async def ask_directly(
        self,
        *,
        q: str,
        message_history: list,
        stream_callback: callable = None,
        reply_ts: float = None,
        **kwargs,
    ):
        """
        Ask directly to the personality.
        """
        # Convert the message history from OpenAI to Anthropic format
        message_history = self.cslack.anthropic_history.openai_to_anthropic(message_history=message_history)
        response = await self.ask.ask(q=q, message_history=message_history, **kwargs)
        return response

    @property
    def description(self):
        return "I do not modify the query. I simply ask the question to Anthropic Claude."

    @property
    def name(self):
        return "Anthropic Claude"
