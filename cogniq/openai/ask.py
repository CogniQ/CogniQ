from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_chat_completion_create

from .chat import system_message, user_message

from .history_augmented_prompt import get_history_augmented_prompt

from .summarize_content import ceil_history, ceil_prompt

from .config import Config
from .agent import agent


async def ask(*, q, message_history=None, bot_id="CogniQ"):
    # logger.info(f"Answering: {q}")
    if message_history is None:
        message_history = [
            system_message(f"Hello, I am {bot_id}, your personal assistant.")
        ]

    # if the history is too long, summarize it
    message_history = ceil_history(message_history)

    # if prompt is too long, summarize it
    short_q = await ceil_prompt(q)

    logger.info("short_q: " + short_q)
    history_augmented_prompt = await get_history_augmented_prompt(
        q=short_q,
        message_history=message_history,
        bot_id=bot_id,
    )

    logger.info("history amended query: " + history_augmented_prompt)
    # message_history.append(user_message(history_augmented_prompt))
    agent_response = agent.run(
        # query=list(reversed(message_history)),
        query=history_augmented_prompt,
        params={
            "Retriever": {"top_k": 3},
        },
    )
    final_answer = agent_response["answers"][0]
    logger.debug(f"final_answer: {final_answer}")
    # transcript = agent_response["transcript"]
    # logger.debug(f"transcript: {transcript}")
    final_answer_text = final_answer.answer
    return final_answer_text
