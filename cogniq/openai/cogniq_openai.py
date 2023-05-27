import logging

logger = logging.getLogger(__name__)

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from .summarizer import Summarizer


class CogniqOpenAI:
    def __init__(self, *, config: dict):
        """
        OpenAI model

        Parameters:
        config (dict): Configuration for the OpenAI model with the following keys:
            OPENAI_API_KEY (str): OpenAI API key.
            OPENAI_CHAT_MODEL (str, optional): OpenAI model to use for chat. Defaults to 'gpt-3.5-turbo'.

            OPENAI_API_TYPE (str, optional): OpenAI API type if using Azure.
            OPENAI_API_BASE (str, optional): OpenAI API base if using Azure.
            OPENAI_API_VERSION (str, optional): OpenAI API version if using Azure.

            # Tuning the prompt and response lengths.
            # There are four components to the prompt/response that should add
            #   up to no more than the maximum context length for the model.
            OPENAI_MAX_TOKENS_HISTORY (int): Context from chat history
            OPENAI_MAX_TOKENS_RETRIEVAL (int): Context from retrieval, such as Bing.
            OPENAI_MAX_TOKENS_PROMPT (int): The text that the user types will be summarized to this length if necessary.
            OPENAI_MAX_TOKENS_RESPONSE (int): Response from OpenAI.
        """

        self.config = config

        # set defaults
        self.config.setdefault("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
        self.config.setdefault("OPENAI_MAX_TOKENS_HISTORY", 800)
        self.config.setdefault("OPENAI_MAX_TOKENS_RETRIEVAL", 700)
        self.config.setdefault("OPENAI_MAX_TOKENS_PROMPT", 1000)
        self.config.setdefault("OPENAI_MAX_TOKENS_RESPONSE", 800)

        # set Azure defaults
        self.config.setdefault("OPENAI_API_TYPE", None)
        self.config.setdefault("OPENAI_API_BASE", None)
        self.config.setdefault("OPENAI_API_VERSION", None)

        # validate required configs
        if not self.config.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is required")

        # initialize summarizer
        self.summarizer = Summarizer(
            config=self.config,
            async_chat_completion_create=self.async_chat_completion_create,
        )

    async def async_chat_completion_create(self, *, messages, **kwargs):
        url = f"https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self.config["OPENAI_CHAT_MODEL"],
            "messages": messages,
            **kwargs,
        }

        return await self.async_openai(url=url, payload=payload, **kwargs)

    async def async_completion_create(self, *, prompt, **kwargs):
        url = f"https://api.openai.com/v1/completions"
        payload = {"prompt": prompt, **kwargs}

        return await self.async_openai(url=url, payload=payload, **kwargs)

    @retry(
        stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=60)
    )
    async def async_openai(self, *, url, payload, **kwargs):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.config["OPENAI_API_KEY"]}',
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    raise Exception(f"Error {response.status}: {await response.text()}")
                else:
                    raise Exception(f"Error {response.status}: {await response.text()}")
