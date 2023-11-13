from __future__ import annotations
from typing import *
import logging

logger = logging.getLogger(__name__)
import json

from cogniq.config import APP_URL, OPENAI_CHAT_MODEL
from cogniq.personalities import BasePersonality
from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack, UserTokenNoneError

from .prompts import retrieval_augmented_prompt
from .functions import get_search_query_function


class SlackSearch(BasePersonality):
    @property
    def description(self) -> str:
        return "I search Slack for relevant conversations."

    @property
    def name(self) -> str:
        return "Slack Search"

    async def ask(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        context: Dict[str, Any],
        stream_callback: Callable[..., None] | None = None,
        reply_ts: float | None = None,
        thread_ts: str | None = None,
    ) -> Dict[str, Any]:
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

        filter = lambda message: self._remove_my_reply_filter(message=message, reply_ts=reply_ts)
        try:
            slack_search_response = await self.cslack.search.search_texts(q=search_query, context=context, filter=filter)
        except UserTokenNoneError as e:
            error_string = f"""USER_NOTIFICATION: Please install the app to use the search personality. The app can be installed at {APP_URL}/slack/install"""
            answer = error_string
            response = {"choices": [{"message": {"content": error_string}}]}
            return {"answer": answer, "response": response}

        logger.debug(f"slack_search_response: {slack_search_response}")

        short_slack_search_response = self.copenai.summarizer.ceil_retrieval(slack_search_response)

        if slack_search_response != short_slack_search_response:
            logger.debug(f"slack_search_response was shortened: {slack_search_response}")

        short_q = await self.copenai.summarizer.ceil_prompt(q)

        prompt = retrieval_augmented_prompt(q=short_q, slack_search_response=short_slack_search_response)

        message_history.append(user_message(prompt))

        response = await self.copenai.async_chat_completion_create(
            messages=message_history,
            stream_callback=stream_callback,
            model=OPENAI_CHAT_MODEL,  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
            stop=["\n\n"],
            temperature=0.2,
        )

        answer = response["choices"][0]["message"]["content"]
        logger.info(f"answer: {answer}")
        return {"answer": answer, "response": response}

    def _remove_my_reply_filter(self, *, message: Dict[str, str], reply_ts: float | None = None) -> bool:
        if not reply_ts:
            return True

        return message["ts"] != reply_ts
