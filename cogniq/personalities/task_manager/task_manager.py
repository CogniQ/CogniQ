from __future__ import annotations
from typing import *
import logging

logger = logging.getLogger(__name__)
import json
import textwrap
import dateutil

from cogniq.config import APP_URL, OPENAI_CHAT_MODEL
from cogniq.personalities import BasePersonality
from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack, UserTokenNoneError

from .functions import schedule_future_message_function
from .task_store import TaskStore


class TaskManager(BasePersonality):
    def __init__(self, cslack: CogniqSlack, copenai: CogniqOpenAI):
        """
        Initialize the BasePersonality.
        :param cslack: CogniqSlack instance.
        """
        self.cslack = cslack
        self.copenai = copenai
        self.task_store = TaskStore()

    @property
    def description(self) -> str:
        return "I am a helpful assistant. I have the ability to schedule messages for later sending."

    @property
    def name(self) -> str:
        return "Task Manager"

    async def async_setup(self) -> None:
        await self.task_store.async_setup()

    def _parse_arguments(self, arguments: str) -> Dict[str, Any] | str:
        try:
            result = json.loads(arguments)
            result['when_time'] = self._parse_date(result['when_time'])
            return result
        except Exception as e:
            logger.error(f"JSON parsing failed for function call arguments: {e}: {arguments}")
            return arguments

    def _parse_date(self, datestring: str) -> datetime:
        try:
            return dateutil.parser.parse(datestring)
        except Exception as e:
            logger.error(f"Date parsing failed for datestring: {e}: {datestring}")
            raise e

    async def ask(
        self,
        *,
        q: str,
        message_history: List[Dict[str, str]],
        context: Dict[str, Any],
        stream_callback: Callable[..., None] | None = None,
        reply_ts: float | None = None,
    ) -> Dict[str, Any]:
        # bot_id = await self.cslack.openai_history.get_bot_user_id(context=context)
        bot_name = await self.cslack.openai_history.get_bot_name(context=context)
        # if the history is too long, summarize it
        message_history = self.copenai.summarizer.ceil_history(message_history)
        message_history = [
            system_message(
                "I don't make assumptions about what values to plug into functions. I ask for clarification if a user request is ambiguous. I only use the functions that I have been provided with. I only use a function if it makes sense to do so."
            ),
        ] + message_history

        tasks_response = await self.copenai.async_chat_completion_create(
            messages=message_history,
            model="gpt-3.5-turbo",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
            function_call="auto",
            functions=[schedule_future_message_function],
        )
        logger.info(f"tasks_response: {tasks_response}")
        tasks_message = tasks_response["choices"][0]
        if tasks_message["message"]["content"]:
            answer = tasks_message["message"]["content"]
        else:
            function_call = tasks_message["message"]["function_call"]
            function_arguments = self._parse_arguments(function_call["arguments"])
            function_name = function_call["name"]

            if function_name == "schedule_future_message":
                future_message = function_arguments["future_message"]
                when_time = function_arguments["when_time"]
                confirmation_response = function_arguments["confirmation_response"]
                logger.info(f"scheduling future message: {future_message} at {when_time}")

                answer = await self.task_store.async_enqueue_task(
                    future_message=future_message,
                    when_time=when_time,
                    confirmation_response=confirmation_response,
                )
            else:
                logger.warning(f"unknown function: {function_name}")
                answer = function_call

        # try:
        #     tasks_dict = json.loads(tasks_full_message["message"]["function_call"]["arguments"])
        # except Exception as e:
        #     logger.warning(f"generation failed: {tasks_full_message}")
        #     return tasks_full_message["message"]["content"]

        # logger.info(f"tasks_dict: {tasks_dict}")
        # if tasks_dict.get("response-clarification"):
        #     answer = tasks_dict["response-clarification"]
        #     # drop the remainder as clarification is called for.
        # elif tasks_dict.get("response-confirmation"):
        #     answer = textwrap.dedent(f"""
        #         {tasks_dict["response-confirmation"]}

        #         ---
        #         The following message will be sent at {tasks_dict["when_time"]}:
        #         {tasks_dict["future_message"]}
        #     """)
        # else:
        #     answer = "I am not sure what you mean. Please try again."

        return {"answer": answer, "response": tasks_response}
        # time_query = ""
        # if tasks_dict.get("on"):
        #     time_query = f'on:{tasks_dict["on"]}'
        # elif tasks_dict.get("during"):
        #     time_query = f'during:{tasks_dict["during"]}'
        # elif tasks_dict.get("after"):
        #     time_query = f'after:{tasks_dict["after"]}'
        # elif tasks_dict.get("before"):
        #     time_query = f'before:{tasks_dict["before"]}'

        # tasks_list = [
        #     " ".join([f'"{phrase}"' for phrase in tasks_dict.get("phrases", [])]),
        #     " ".join([f'-"{word}"' for word in tasks_dict.get("negative_words", [])]),
        #     f'in:{tasks_dict["in"]}' if tasks_dict.get("in") else "",
        #     f'from:{tasks_dict["from"]}' if tasks_dict.get("from") else "",
        #     f'with:{tasks_dict["with"]}' if tasks_dict.get("with") else "",
        #     f'has:{tasks_dict["has"]}' if tasks_dict.get("has") else "",
        #     time_query,
        #     "is:thread" if tasks_dict.get("is_thread", False) else "",
        # ]

        # tasks = " ".join(tasks_list)

        # logger.info(f"searching slack with tasks: {tasks}")

        # filter = lambda message: self._remove_my_reply_filter(message=message, reply_ts=reply_ts)
        # try:
        #     slack_search_response = await self.cslack.search.search_texts(q=tasks, context=context, filter=filter)
        # except UserTokenNoneError as e:
        #     error_string = f"""USER_NOTIFICATION: Please install the app to use the search personality. The app can be installed at {APP_URL}/slack/install"""
        #     answer = error_string
        #     response = {"choices": [{"message": {"content": error_string}}]}
        #     return {"answer": answer, "response": response}

        # logger.debug(f"slack_search_response: {slack_search_response}")

        # short_slack_search_response = self.copenai.summarizer.ceil_retrieval(slack_search_response)

        # if slack_search_response != short_slack_search_response:
        #     logger.debug(f"slack_search_response was shortened: {slack_search_response}")

        # short_q = await self.copenai.summarizer.ceil_prompt(q)

        # prompt = retrieval_augmented_prompt(q=short_q, slack_search_response=short_slack_search_response)

        # message_history.append(user_message(prompt))

        # response = await self.copenai.async_chat_completion_create(
        #     messages=message_history,
        #     stream_callback=stream_callback,
        #     model=OPENAI_CHAT_MODEL,  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        #     stop=["\n\n"],
        #     temperature=0.2,
        # )

        # answer = response["choices"][0]["message"]["content"]
        # logger.info(f"answer: {answer}")
        return {"answer": answer, "response": tasks_response}

    def _remove_my_reply_filter(self, *, message: Dict[str, str], reply_ts: float | None = None) -> bool:
        if not reply_ts:
            return True

        return message["ts"] != reply_ts
