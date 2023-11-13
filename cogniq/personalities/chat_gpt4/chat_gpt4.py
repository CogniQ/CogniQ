from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)


from cogniq.personalities import BasePersonality
from cogniq.slack import CogniqSlack
from cogniq.openai import system_message, user_message, CogniqOpenAI


class ChatGPT4(BasePersonality):
    @property
    def description(self) -> str:
        return "I do not modify the query, and simply ask the question to ChatGPT 4."

    @property
    def name(self) -> str:
        return "ChatGPT4"

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
        if message_history is None:
            message_history = []

        message_history.append(user_message(q))

        res = await self.copenai.async_chat_completion_create(
            messages=message_history,
            stream_callback=stream_callback,
            model="gpt-4",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        answer = res["choices"][0]["message"]["content"]
        logger.info(f"final_answer: {answer}")
        return {"answer": answer, "response": res}
