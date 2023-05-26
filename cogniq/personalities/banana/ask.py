from cogniq.openai import system_message, user_message, assistant_message, CogniqOpenAI
from cogniq.slack import CogniqSlack

import logging


class Ask:
    def __init__(
        self,
        *,
        config: dict,
        logger: logging.Logger,
        cslack: CogniqSlack,
        copenai: CogniqOpenAI,
        **kwargs,
    ):
        """
        Ask subclass of the ChatGPT4 personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, logger=logger, cslack=cslack, copenai=copenai)
        await ask.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Chat GPT4 personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.

        logger (logging.Logger): Logger to log information about the app's status.
        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.

        """
        self.logger = logger
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
                f"Hello, I am {self.bot_name}. I am a slack bot that will always say banana, no matter the question."
            ),
            user_message(q),
            assistant_message("banana"),
            user_message("What is the meaning of life?"),
            assistant_message("banana"),
            user_message("Who shot JFK?"),
            assistant_message("banana"),
        ] + message_history

        message_history.append(user_message(q))

        answer = await self.copenai.async_chat_completion_create(
            messages=message_history,
            model="gpt-3.5-turbo",  # [gpt-4-32k, gpt-4, gpt-3.5-turbo]
        )

        final_answer = answer["choices"][0]["message"]["content"]
        self.logger.info(f"final_answer: {final_answer}")
        return final_answer
