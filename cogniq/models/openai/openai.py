from cogniq.logging import setup_logger
logger = setup_logger(__name__)

from .async_chat_completion_create import async_chat_completion_create


def message(role, content):
    return {"role": f"{role}", "content": f"{content}"}


def user_message(content):
    return message("user", content)


def system_message(content):
    return message("system", content)

def assistant_message(content):
    return message("assistant", content)


async def ask(*, q, message_history=None, context=[]):
    if message_history is None:
        message_history = [
            system_message("Hello, I am CogniQ, your personal assistant.")
        ]
    message_history.append(user_message(q))
    response = await async_chat_completion_create(
        messages=message_history,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n", " Human:", " AI:"],
    )
    # logger.debug(f"response: {response}")
    return response["choices"][0]["message"]["content"]
