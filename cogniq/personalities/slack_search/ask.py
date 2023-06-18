from __future__ import annotations
from typing import *

import json
import logging

logger = logging.getLogger(__name__)


from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack

from .prompts import retrieval_augmented_prompt
from .functions import get_search_query_function


class Ask:
    def __init__(
        self,
        *,
        config: dict,
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

    async def async_setup(self):
        """
        Call me after initialization, please!
        """
        pass

    async def ask(self, *, q: str, message_history: list[dict[str,str]], stream_callback: callable = None, context: dict):
        # bot_id = await self.cslack.openai_history.get_bot_user_id(context=context)
        bot_name = await self.cslack.openai_history.get_bot_name(context=context)
        # if the history is too long, summarize it
        message_history = self.copenai.summarizer.ceil_history(message_history)

        message_history = [
            system_message(
                "I am an expert at using Slack's keyword and phrase search to search Slack for the relevant context to answer your question. I have the capabilities to access and retrieve historic slack messages."
            ),
        ] + message_history

        search_query_response = await self.copenai.async_chat_completion_create(
            messages=message_history,
            model="gpt-3.5-turbo-0613",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
            function_call={"name": "get_search_query"},
            functions=[get_search_query_function],
        )

        search_query_full_message = search_query_response["choices"][0]
        try:
            search_query_dict = json.loads(search_query_full_message["message"]["function_call"]["arguments"])
        except Exception as e:
            logger.warning(f"search query generation failed: {search_query_full_message}")
            return search_query_full_message["message"]["content"]

        logger.info(f"search_query_dict: {search_query_dict}")

        time_query = ""
        if search_query_dict.get("on"):
            time_query = f'on:{search_query_dict["on"]}'
        elif search_query_dict.get("during"):
            time_query = f'during:{search_query_dict["during"]}'
        elif search_query_dict.get("after"):
            time_query = f'after:{search_query_dict["after"]}'
        elif search_query_dict.get("before"):
            time_query = f'before:{search_query_dict["before"]}'

        search_query_list = [
            " ".join([f'"{phrase}"' for phrase in search_query_dict.get("phrases", [])]),
            " ".join([f'-"{word}"' for word in search_query_dict.get("negative_words", [])]),
            f'in:{search_query_dict["in"]}' if search_query_dict.get("in") else "",
            f'from:{search_query_dict["from"]}' if search_query_dict.get("from") else "",
            f'with:{search_query_dict["with"]}' if search_query_dict.get("with") else "",
            f'has:{search_query_dict["has"]}' if search_query_dict.get("has") else "",
            time_query,
            "is:thread" if search_query_dict.get("is_thread", False) else "",
        ]

        search_query = " ".join(search_query_list)

        logger.info(f"searching slack with search_query: {search_query}")

        slack_search_response = await self.cslack.search.search_texts(q=search_query, context=context)

        logger.debug(f"slack_search_response: {slack_search_response}")

        short_slack_search_response = self.copenai.summarizer.ceil_history(slack_search_response)

        if slack_search_response != short_slack_search_response:
            logger.debug(f"slack_search_response was shortened: {slack_search_response}")

        short_q = await self.copenai.summarizer.ceil_prompt(q)

        prompt = retrieval_augmented_prompt(q=short_q, slack_search_response=short_slack_search_response)

        # logger.info(f"Retrieval augmented prompt: {prompt}")

        # If prompt is too long, summarize it
        short_prompt = await self.copenai.summarizer.ceil_prompt(prompt)

        if prompt != short_prompt:
            logger.info(f"Original prompt: {prompt}")
            logger.info(f"Evaluating shortened prompt: {short_prompt}")
        else:
            logger.info(f"Evaluating prompt: {short_prompt}")

        message_history.append(user_message(prompt))

        answer = await self.copenai.async_chat_completion_create(
            messages=message_history,
            stream_callback=stream_callback,
            model=self.config["OPENAI_CHAT_MODEL"],  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        final_answer = answer["choices"][0]["message"]["content"]
        logger.info(f"final_answer: {final_answer}")
        return final_answer
