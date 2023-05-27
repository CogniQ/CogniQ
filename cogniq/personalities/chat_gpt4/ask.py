import logging

logger = logging.getLogger(__name__)

from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack




class Ask:
    def __init__(
        self,
        *,
        config: dict,
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
        **kwargs,
    ):
        """
        Ask subclass of the ChatGPT4 personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, cslack=cslack, copenai=copenai)
        await ask.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat GPT4 personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.


        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.

        """

        self.config = config
        self.cslack = cslack
        self.copenai = copenai

    async def async_setup(self):
        """
        Call me after initialization, please!
        """
        self.bot_id = await self.cslack.openai_history.get_bot_user_id()
        self.bot_name = await self.cslack.openai_history.get_bot_name()

    async def ask(self, *, q, message_history=[]):
        # logger.info(f"Answering: {q}")

        # if the history is too long, summarize it
        message_history = self.copenai.summarizer.ceil_history(message_history)

        # Set the system message
        message_history = [
            system_message(
                f"Hello, I am {self.bot_name}. I am a slack bot that can answer your questions."
            )
        ] + message_history

        # if prompt is too long, summarize it
        short_q = await self.copenai.summarizer.ceil_prompt(q)

        logger.info("short_q: " + short_q)
        message_history.append(user_message(short_q))

        answer = await self.copenai.async_chat_completion_create(
            messages=message_history,
            model="gpt-4",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        final_answer = answer["choices"][0]["message"]["content"]
        logger.info(f"final_answer: {final_answer}")
        return final_answer
