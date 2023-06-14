import logging

logger = logging.getLogger(__name__)

import asyncio
from typing import List
from slack_bolt.async_app import AsyncApp
from slack_sdk.errors import SlackApiError

from cogniq.openai import user_message, system_message, assistant_message

from .base_history import BaseHistory


class OpenAIHistory(BaseHistory):
    def __init__(self, app: AsyncApp):
        """
        History is intended as a subclass of CogniqSlack when interoperating with OpenAI.
        It is responsible for storing and retrieving slack history formatted for OpenAI's consumption.

        Parameters:
        app (slack_bolt.async_app.AsyncApp): Instance of Slack's AsyncApp.

        logger (logging.Logger): Logger to log information about the history object.
        """
        self.app = app

    async def get_bot_user_id(self, *, context: dict) -> str:
        return context["bot_user_id"]

    async def get_bot_name(self, *, context: dict) -> str:
        auth_test = await self.app.client.auth_test(token=context["bot_token"])
        return auth_test["user"]

    async def get_history(self, *, event: dict, context: dict):
        channel_id = event["channel"]
        thread_ts = event.get("thread_ts")

        response = await self._get_conversations_and_convert_to_chat_sequence(channel_id=channel_id, thread_ts=thread_ts, context=context)

        logger.debug(f"History: {response}")
        return response

    async def _get_conversations_and_convert_to_chat_sequence(self, *, channel_id: str, thread_ts=None, context: dict):
        messages = await self._get_conversations(channel_id=channel_id, thread_ts=thread_ts, context=context)

        bot_user_id = await self.get_bot_user_id(context=context)

        # If thread_ts is None, it means we fetched the conversation history.
        # We need to reverse this to make it chronological ascending.
        if thread_ts is None:
            messages = reversed(messages)

        return self._convert_to_chat_sequence(messages=messages, bot_user_id=bot_user_id)

    async def _get_conversations(self, *, channel_id: str, thread_ts=None, context: dict):
        messages = []
        cursor = None
        messages_per_page = 20
        max_messages = 20

        while True:
            try:
                if thread_ts is None:
                    # Fetch conversation history
                    response = await self.app.client.conversations_history(
                        token=context["bot_token"],
                        channel=channel_id,
                        limit=messages_per_page,
                        cursor=cursor,
                    )
                else:
                    # Fetch conversation replies
                    response = await self.app.client.conversations_replies(
                        token=context["bot_token"],
                        channel=channel_id,
                        limit=messages_per_page,
                        ts=thread_ts,
                        cursor=cursor,
                    )
            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    # logger.info(f"history fetched thus far: {messages}")
                    # logger.info(f"Response: {e.response}")
                    logger.warning(f"Rate limit hit. Retrying after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    logger.error(f"Error fetching conversations due to Slack API Error: {e}")
                    return messages

            # logger.info("History Response: %s", response)
            for message in response["messages"]:
                filtered_message = self._filter_message(message)
                # If there is a thread in the conversation history, fetch the thread.
                if thread_ts is None and filtered_message.get("thread_ts") is not None:
                    replies_response = await self._get_conversations(
                        channel_id=channel_id,
                        thread_ts=filtered_message.get("thread_ts"),
                        context=context,
                    )
                    filtered_message["replies"] = replies_response
                messages.append(filtered_message)

            if not response["has_more"]:
                break
            if len(messages) >= max_messages:
                break
            logger.info(f"fetching next cursor: {response['response_metadata']['next_cursor']}")
            cursor = response["response_metadata"]["next_cursor"]
        return messages

    def _filter_message(self, message):
        return {
            "ts": message.get("ts"),
            "user": message.get("user"),
            "text": message.get("text"),
            "thread_ts": message.get("thread_ts"),
        }

    def _convert_to_chat_sequence(self, *, messages, bot_user_id):
        chat_sequence = []
        for message in messages:
            if message.get("user") == bot_user_id:
                chat_sequence.append(assistant_message(message.get("text")))
            else:
                chat_sequence.append(user_message(message.get("text")))
            if message.get("replies"):
                for reply in message.get("replies"):
                    if reply.get("user") == bot_user_id:
                        chat_sequence.append(assistant_message(reply.get("text")))
                    else:
                        chat_sequence.append(user_message(reply.get("text")))
        return chat_sequence
