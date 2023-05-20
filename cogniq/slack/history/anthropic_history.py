from typing import List
from slack_bolt.async_app import AsyncApp
import logging
from slack_sdk.errors import SlackApiError
import asyncio

from .openai_history import OpenAIHistory


class AnthropicHistory(OpenAIHistory):
    def _convert_to_chat_sequence(self, *, messages, bot_user_id):
        chat_sequence = ""
        for message in messages:
            if message.get("user") == bot_user_id:
                chat_sequence += f"\n\nAssistant: {message.get('text')}"
            else:
                chat_sequence += f"\n\nHuman: {message.get('text')}"
            if message.get("replies"):
                for reply in message.get("replies"):
                    if reply.get("user") == bot_user_id:
                        chat_sequence += f"\n\nAssistant: {reply.get('text')}"
                    else:
                        chat_sequence += f"\n\nHuman: {reply.get('text')}"
        return chat_sequence
