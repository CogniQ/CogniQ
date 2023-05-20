from cogniq.openai import system_message, user_message, CogniqOpenAI
from cogniq.slack import CogniqSlack

import logging

from .prompts import agent_prompt
from .custom_web_qa_pipeline import CustomWebQAPipeline


from haystack.nodes import PromptNode, PromptTemplate

# For the pipeline to work, you'd need to import the Reader, Retriever, and DocumentStore
# This example skips the pipeline configuration steps
from haystack.agents import Agent, Tool
from haystack.agents.base import ToolsManager
from haystack.nodes import PromptNode, PromptTemplate


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
        Ask subclass of BingSearch personality
        Please call async_setup before using this class, please!

        ```
        ask = Ask(config=config, logger=logger, cslack=cslack, copenai=copenai)
        await ask.async_setup()
        ```

        Parameters:
        config (dict): Configuration for the Bing Search personality with the following keys:
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens to generate for the response.
            OPENAI_API_KEY (str): OpenAI API key.
            BING_SUBSCRIPTION_KEY (str): Bing subscription key.



        logger (logging.Logger): Logger to log information about the app's status.
        cslack (CogniqSlack): CogniqSlack instance.
        copenai (CogniqOpenAI): CogniqOpenAI instance.
        """
        self.logger = logger
        self.config = config
        self.cslack = cslack
        self.copenai = copenai

        self.web_qa_tool = Tool(
            name="Search",
            pipeline_or_node=CustomWebQAPipeline(config=config, logger=logger),
            description="useful for when you need to Google questions.",
            output_variable="answers",
        )

        agent_template = PromptTemplate("few-shot-react", prompt_text=agent_prompt)

        agent_prompt_node = PromptNode(
            "gpt-3.5-turbo",
            api_key=self.config["OPENAI_API_KEY"],
            max_length=self.config["OPENAI_MAX_TOKENS_RESPONSE"],
            stop_words=["Observation:"],
        )

        self.agent = Agent(
            prompt_node=agent_prompt_node,
            prompt_template=agent_template,
            tools_manager=ToolsManager([self.web_qa_tool]),
        )

    async def async_setup(self):
        """
        Call me after initialization, please!
        """
        self.bot_id = await self.cslack.openai_history.get_bot_user_id()
        self.bot_name = await self.cslack.openai_history.get_bot_name()

    async def ask(self, *, q, message_history=[]):
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

        self.logger.info("short_q: " + short_q)
        history_augmented_prompt = await self.get_history_augmented_prompt(
            q=short_q,
            message_history=message_history,
        )

        self.logger.info("history amended query: " + history_augmented_prompt)
        # message_history.append(user_message(history_augmented_prompt))
        agent_response = self.agent.run(
            # query=list(reversed(message_history)),
            query=history_augmented_prompt,
            params={
                "Retriever": {"top_k": 3},
            },
        )
        final_answer = agent_response["answers"][0]
        self.logger.debug(f"final_answer: {final_answer}")
        # transcript = agent_response["transcript"]
        # logger.debug(f"transcript: {transcript}")
        final_answer_text = final_answer.answer
        return final_answer_text

    def history_augmented_prompt(self, *, q):
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

    async def get_history_augmented_prompt(self, *, q, message_history):
        history_augmented_message_history = message_history.copy()
        history_augmented_message_history.append(
            user_message(self.history_augmented_prompt(q=q))
        )
        response = await self.copenai.async_chat_completion_create(
            messages=history_augmented_message_history,
            temperature=0.7,
            max_tokens=self.config["OPENAI_MAX_TOKENS_RESPONSE"],
            top_p=1,
            frequency_penalty=0,  # scales down the log probabilities of words that the model has seen frequently during training
            presence_penalty=0,  # modifies the probability distribution to make less likely words that were present in the input prompt or seed text
        )
        answer = response["choices"][0]["message"]["content"].strip()
        self.logger.debug(f"modifying query for history: {answer}")
        return answer
