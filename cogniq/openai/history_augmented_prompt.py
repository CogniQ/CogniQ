from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from .api import async_chat_completion_create
from .chat import system_message, user_message, assistant_message
from ..personalities.bing_search.config import Config


def history_augmented_prompt(*, q):
    return f"""Please rephrase the Query in a way that an information retrieval system can provide an answer.

    Examples:
    ##
    Query: "why is that the case?"
    Response: "Why is it the case that the sky is blue?"
    ##
    Query: "tell me more"
    Response: "Tell me more about the weather in Seattle and how it is often rainy."
    ##
    Query: {q}
    Response:"""


async def get_history_augmented_prompt(*, q, message_history, bot_id):
    history_augmented_message_history = message_history.copy()
    history_augmented_message_history.append(
        user_message(history_augmented_prompt(q=q))
    )
    response = await async_chat_completion_create(
        messages=history_augmented_message_history,
        temperature=0.7,
        max_tokens=Config["OPENAI_MAX_TOKENS_RESPONSE"],
        top_p=1,
        frequency_penalty=0,  # scales down the log probabilities of words that the model has seen frequently during training
        presence_penalty=0,  # modifies the probability distribution to make less likely words that were present in the input prompt or seed text
    )
    answer = response["choices"][0]["message"]["content"].strip()
    logger.debug(f"modifying query for history: {answer}")
    return answer
