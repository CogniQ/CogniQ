from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.openai import ask

from cogniq.slack import CogniqSlack

async def ask_openai_task(*, event, reply_ts, cslack: CogniqSlack):
    channel = event["channel"]
    message = event["text"]
    bot_id = event.get("bot_id")
    history = await cslack.history.fetch_history(event=event)
    # logger.debug(f"history: {history}")

    openai_response = await ask(q=message, message_history=history, bot_id=bot_id)
    # logger.debug(openai_response)
    await cslack.app.client.chat_update(
        channel=channel, ts=reply_ts, text=openai_response
    )



from cogniq.openai.chat import system_message, user_message

from cogniq.openai.history_augmented_prompt import get_history_augmented_prompt

from cogniq.openai.summarize_content import ceil_history, ceil_prompt

from cogniq.openai.api import async_chat_completion_create

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
    message_history.append(user_message(short_q))
    
    answer = await async_chat_completion_create(
        messages=message_history,
        model="gpt-4", # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
    )

    final_answer = answer["choices"][0]["message"]["content"]
    logger.info(f"final_answer: {final_answer}")
    return final_answer
