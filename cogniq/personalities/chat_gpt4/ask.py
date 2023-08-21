from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from wandb.sdk.data_types.trace_tree import Trace

from cogniq.personalities import BaseAsk
from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack
from cogniq.wandb import WandbChildSpan


class Ask(BaseAsk):
    def __init__(
        self,
        *,
        config: Dict[str, str],
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
        **kwargs,
    ):
        """
        Ask subclass of the ChatGPT4 personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, cslack=cslack, copenai=copenai)
        await ask.async_setup()
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

    async def async_setup(self) -> None:
        """
        Call me after initialization, please!
        """
        pass

    async def ask(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        stream_callback: Callable[..., None] | None = None,
        context: Dict,
        parent_span: Trace,
    ) -> Dict[str, Any]:
        with WandbChildSpan(parent_span=parent_span, name="chat_gpt4", kind="chain") as span:
            message_history = message_history or []
            # bot_id = await self.cslack.openai_history.get_bot_user_id(context=context)
            bot_name = await self.cslack.openai_history.get_bot_name(context=context)
            # logger.info(f"Answering: {q}")

            # if the history is too long, summarize it
            message_history = self.copenai.summarizer.ceil_history(message_history)

            # Set the system message
            message_history = [
                system_message(f"Hello, I am {bot_name}. I am a slack bot that can answer your questions.")
            ] + message_history

            # if prompt is too long, summarize it
            short_q = await self.copenai.summarizer.ceil_prompt(q)

            logger.info("short_q: " + short_q)
            message_history.append(user_message(short_q))

            res = await self.copenai.async_chat_completion_create(
                messages=message_history,
                stream_callback=stream_callback,
                model="gpt-4",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
            )

            answer = res["choices"][0]["message"]["content"]
            logger.info(f"final_answer: {answer}")
            span.add_inputs_and_outputs(inputs={"query": q}, outputs={"answer": answer})
            return {"answer": answer, "response": res}
