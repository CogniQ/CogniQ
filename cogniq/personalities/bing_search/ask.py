from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.slack import CogniqSlack


async def ask_task(*, event, reply_ts, cslack: CogniqSlack):
    channel = event["channel"]
    message = event["text"]
    bot_id = await cslack.history.get_bot_user_id()
    history = await cslack.history.get_history(event=event)
    # logger.debug(f"history: {history}")

    openai_response = await ask(q=message, message_history=history, bot_id=bot_id)
    # logger.debug(openai_response)
    await cslack.app.client.chat_update(
        channel=channel, ts=reply_ts, text=openai_response
    )


from cogniq.openai.chat import system_message, user_message

from cogniq.openai.history_augmented_prompt import get_history_augmented_prompt

from cogniq.openai.summarize_content import ceil_history, ceil_prompt

from cogniq.personalities.bing_search.agent import agent


async def ask(*, q, message_history=[], bot_id="CogniQ"):
    # if the history is too long, summarize it
    message_history = ceil_history(message_history)

    # Set the system message
    message_history = [
        system_message(
            f"Hello, I am {bot_id}. I am a slack bot that can answer your questions."
        )
    ] + message_history

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
