from cogniq.logging import setup_logger

logger = setup_logger(__name__)

from cogniq.slack import CogniqSlack
import os


async def ask_task(*, event, reply_ts, cslack: CogniqSlack):
    channel = event["channel"]
    message = event["text"]
    bot_id = await cslack.history.get_bot_user_id()
    history = await cslack.history.get_history(event=event)
    logger.debug(f"history: {history}")

    response = await ask(q=message, message_history=history, bot_id=bot_id)
    await cslack.app.client.chat_update(channel=channel, ts=reply_ts, text=response)


from haystack.nodes.prompt.invocation_layer import AnthropicClaudeInvocationLayer


async def ask(*, q, message_history="", bot_id="CogniQ"):
    kwargs = {
        "model": "claude-instant-v1-100k",
        "max_tokens_to_sample": 100000,
        "temperature": 1,
        "top_p": -1,  # disabled
        "top_k": -1,
        "stop_sequences": ["\n\nHuman: "],
        "stream": False,
    }

    api_key = os.environ["ANTHROPIC_API_KEY"]
    layer = AnthropicClaudeInvocationLayer(api_key=api_key, **kwargs)
    newprompt = f"{message_history}\n\nHuman: {q}"
    res = layer.invoke(prompt=newprompt)

    logger.info(f"res: {res}")
    return "".join(res)
