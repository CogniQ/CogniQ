from .chat import system_message, user_message

import tiktoken


class Summarizer:
    def __init__(self, *, config, async_chat_completion_create, logger):
        """
        Summarizer is intended as a subclass of CogniqOpenAI and is responsible for managing context window.

        Parameters:
        config (dict): Configuration dictionary with the following keys:
            OPENAI_CHAT_MODEL (str): OpenAI model to use for chat.
            OPENAI_MAX_TOKENS_HISTORY (int): Context from chat history
            OPENAI_MAX_TOKENS_RETRIEVAL (int): Context from retrieval, such as Bing.
            OPENAI_MAX_TOKENS_PROMPT (int): The text that the user types will be summarized to this length if necessary.
            OPENAI_MAX_TOKENS_RESPONSE (int): Response from OpenAI.

        async_chat_completion_create (function): Function to create a chat completion.
        logger (logging.Logger): Logger to log information about the app's status.
        """
        self.config = config
        self.async_chat_completion_create = async_chat_completion_create
        self.logger = logger

        self.encoding = tiktoken.encoding_for_model(self.config["OPENAI_CHAT_MODEL"])

    def encode(self, text):
        return self.encoding.encode(text)

    def count_tokens(self, text):
        simple_coerced_string = str(text)
        return len(self.encode(simple_coerced_string))

    def ceil_history(self, message_history):
        simple_coerced_string = str(message_history)
        total_tokens = self.count_tokens(simple_coerced_string)
        max_tokens = self.config["OPENAI_MAX_TOKENS_HISTORY"]

        while total_tokens > max_tokens:
            message_history.pop(0)
            simple_coerced_string = str(message_history)
            total_tokens = self.count_tokens(simple_coerced_string)

        return message_history

    def ceil_retrieval(self, retrieval):
        simple_coerced_string = str(retrieval)
        total_tokens = self.count_tokens(simple_coerced_string)
        max_tokens = self.config["OPENAI_MAX_TOKENS_RETRIEVAL"]

        while total_tokens > max_tokens:
            retrieval = retrieval[:-1]  # removed last message
            simple_coerced_string = str(retrieval)
            total_tokens = self.count_tokens(simple_coerced_string)

        return retrieval

    async def ceil_prompt(self, prompt):
        simple_coerced_string = str(prompt)
        if (
            self.count_tokens(simple_coerced_string)
            > self.config["OPENAI_MAX_TOKENS_PROMPT"]
        ):
            return await self.summarize_content(
                simple_coerced_string, self.config["OPENAI_MAX_TOKENS_PROMPT"]
            )
        else:
            return prompt

    async def summarize_content(self, content, max_tokens):
        response = await self.async_chat_completion_create(
            messages=[
                system_message(
                    "Please summarize the following content within the token limit."
                ),
                user_message(content),
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0,
        )
        answer = response["choices"][0]["message"]["content"].strip()
        return answer
