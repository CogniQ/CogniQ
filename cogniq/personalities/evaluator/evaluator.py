import asyncio

from functools import partial

from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import CogniqOpenAI

from .ask import Ask


class Buffer:
    def __init__(self):
        self.text = ""


class Evaluator(BasePersonality):
    def __init__(self, *, config: dict, cslack: CogniqSlack, copenai: CogniqOpenAI, **kwargs):
        """
        Evaluator personality
        Please call async_setup after initializing the personality.

        ```
        evaluator = Evaluator(config=config, copenai=copenai)
        await evaluator.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat GPT4 personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.


        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.
        """
        self.config = config
        self.cslack = cslack
        self.copenai = copenai

        self.ask = Ask(config=config, cslack=cslack, copenai=copenai)

    async def async_setup(self):
        """
        Please call after initializing the personality.
        """
        await self.ask.async_setup()

    async def ask_task(self, *, event, reply_ts, personalities, context):
        """
        Executes the ask_task against all the personalities and returns the best or compiled response.
        """
        channel = event["channel"]
        message = event["text"]

        # create a buffer for each personality
        response_buffers = {p.name: Buffer() for p in personalities}
        for name, buf in response_buffers.items():
            buf.text += f"-------------------------\n{name} Stream of Thought:\n"

        buffer_post_end = asyncio.Event()

        def stream_callback(name, token, **kwargs):
            setattr(response_buffers[name], "text", response_buffers[name].text + token)

        # Wrap personalities and their callbacks in a dict of dicts
        personalities = {p.name: {"object": p, "stream_callback": partial(stream_callback, p.name)} for p in personalities}

        buffer_post_end = asyncio.Event()  # event flag for ending the buffer_and_post loop
        buffer_and_post_task = asyncio.create_task(
            self.buffer_and_post(response_buffers, channel, reply_ts, 1, buffer_post_end)
        )  # posts every 0.25 seconds
        message_history = await self.cslack.openai_history.get_history(event=event)

        openai_response = await self.ask.ask(
            q=message,
            message_history=message_history,
            personalities=personalities,
            context=context,
        )
        buffer_post_end.set()  # end the buffer_and_post loop
        await buffer_and_post_task  # ensure buffer_and_post task is finished
        await self.cslack.chat_update(channel=channel, ts=reply_ts, text=openai_response)

    async def buffer_and_post(self, buffers, channel, reply_ts, interval, buffer_post_end):
        while not buffer_post_end.is_set():
            combined_text = "\n".join(buf.text for buf in buffers.values())
            if combined_text:
                await self.cslack.chat_update(
                    channel=channel,
                    ts=reply_ts,
                    text=combined_text,
                    retry_on_rate_limit=False,
                )
            await asyncio.sleep(interval)

    async def ask_directly(self, *, q, message_history, personalities, context, **kwargs):
        """
        Ask directly to the personality.
        """
        response = await self.ask.ask(q=q, message_history=message_history, personalities=personalities, context=context, **kwargs)
        return response

    @property
    def description(self):
        return "I evaluate the responses from the other personalities and return the best one."

    @property
    def name(self):
        return "Evaluator"
