from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import asyncio
from concurrent.futures import ThreadPoolExecutor as PoolExecutor

from cogniq.personalities import BaseAsk
from cogniq.openai import (
    system_message,
    user_message,
    assistant_message,
    message_to_string,
    CogniqOpenAI,
)
from cogniq.slack import CogniqSlack


from .prompts import agent_prompt
from .custom_web_qa_pipeline import CustomWebQAPipeline


# For the pipeline to work, you'd need to import the Reader, Retriever, and DocumentStore
# This example skips the pipeline configuration steps
from haystack.agents import Agent, Tool
from haystack.agents.base import ToolsManager
from haystack.nodes import PromptNode


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
        Ask subclass of BingSearch personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, cslack=cslack, copenai=copenai)
        await ask.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Bing Search personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.
            BING_SUBSCRIPTION_KEY (str): Bing subscription key.

        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.
        """

        self.config = config
        self.cslack = cslack
        self.copenai = copenai

        self.web_qa_tool = Tool(
            name="Search",
            pipeline_or_node=CustomWebQAPipeline(config=config),
            description="useful for when you need to Google questions.",
            output_variable="answers",
        )

        self.agent_prompt_node = PromptNode(
            "gpt-3.5-turbo",
            api_key=self.config["OPENAI_API_KEY"],
            max_length=self.config["OPENAI_MAX_TOKENS_RESPONSE"],
            stop_words=["Observation:"],
        )

    async def async_setup(self) -> None:
        """
        Call me after initialization, please!
        """
        pass

    def agent_run(self, query: str, stream_callback: Callable[..., None] | None = None) -> Dict[str, Any]:
        agent = Agent(
            prompt_node=self.agent_prompt_node,
            prompt_template=agent_prompt,
            tools_manager=ToolsManager([self.web_qa_tool]),
            max_steps=4,
            streaming=False,  # Disable the native streaming callback
        )
        agent.callback_manager.on_new_token = stream_callback
        return agent.run(
            query=query,
            params={
                "Retriever": {"top_k": 3},
            },
        )

    async def ask(
        self, *, q: str, message_history: List[Dict[str, str]], stream_callback: Callable[..., None] | None = None, context: Dict
    ) -> Dict[str, Any]:
        # bot_id = await self.cslack.openai_history.get_bot_user_id(context=context)
        bot_name = await self.cslack.openai_history.get_bot_name(context=context)
        if message_history == None:
            message_history = []
        # if the history is too long, summarize it
        message_history = self.copenai.summarizer.ceil_history(message_history)

        # Set the system message
        message_history = [system_message(f"Hello, I am {bot_name}. I am a slack bot that can answer your questions.")] + message_history

        # if prompt is too long, summarize it
        short_q = await self.copenai.summarizer.ceil_prompt(q)

        logger.info("short_q: " + short_q)
        history_augmented_prompt = await self.get_history_augmented_prompt(
            q=short_q,
            message_history=message_history,
        )

        logger.info("history amended query: " + history_augmented_prompt)

        loop = asyncio.get_event_loop()
        with PoolExecutor() as executor:
            agent_response_task = loop.run_in_executor(
                executor,
                self.agent_run,
                history_augmented_prompt,
                stream_callback,
            )
            agent_response = await agent_response_task
        final_answer = agent_response["answers"][0]
        logger.debug(f"final_answer: {final_answer}")
        final_answer_text = final_answer.answer
        if not final_answer_text:
            transcript = agent_response["transcript"]
            summarized_transcript = await self.copenai.summarizer.summarize_content(transcript, self.config["OPENAI_MAX_TOKENS_RESPONSE"])
            final_answer_text = summarized_transcript
        return { "answer": final_answer_text, "response": agent_response }

    async def get_history_augmented_prompt(self, *, q: str, message_history: List[Dict[str, str]]) -> str:
        """
        Returns a prompt augmented with the message history.
        """
        history = ("\n\n".join([message_to_string(message) for message in message_history]),)
        prompt = f"""Conversation history: {history}

        Query: {q}"""
        return prompt
