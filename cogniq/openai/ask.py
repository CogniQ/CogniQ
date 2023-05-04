from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_chat_completion_create

from .chat import system_message, user_message

from .retrieval_augmentation import get_retrieval_augmented_prompt

from .summarize_content import ceil_history, ceil_prompt

from .config import Config


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

    retrieval_augmented_prompt = await get_retrieval_augmented_prompt(
        q=short_q,
        message_history=message_history,
        bot_id=bot_id,
    )

    message_history.append(user_message(retrieval_augmented_prompt))
    logger.info(f"asking question: {retrieval_augmented_prompt}")
    # logger.debug(f"message_history: {message_history}")
    response = await async_chat_completion_create(
        messages=message_history,
        temperature=0.7,
        max_tokens=Config["OPENAI_MAX_TOKENS_RESPONSE"],
        top_p=1,
        frequency_penalty=0,  # scales down the log probabilities of words that the model has seen frequently during training
        presence_penalty=0,  # modifies the probability distribution to make less likely words that were present in the input prompt or seed text
    )
    answer = response["choices"][0]["message"]["content"].strip()
    logger.info(f"response: {answer}")
    # logger.debug(f"response: {response}")
    return answer
