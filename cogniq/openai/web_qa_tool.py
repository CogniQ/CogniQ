from cogniq.logging import setup_logger

logger = setup_logger(__name__)


from .config import Config


from cogniq.bing import web_retriever


from haystack.agents import Tool
from haystack.pipelines import BaseStandardPipeline

from haystack.nodes.retriever.web import WebRetriever
from haystack.nodes import (
    PromptTemplate,
    PromptNode,
    Shaper,
    TopPSampler,
)
from haystack.pipelines.base import Pipeline
from haystack.nodes.prompt.shapers import AnswerParser

from typing import Optional


class CustomWebQAPipeline(BaseStandardPipeline):
    """
    Pipeline for Generative Question Answering performed based on Documents returned from a web search engine.
    """

    def __init__(self):
        """
        :param retriever: The WebRetriever used for retrieving documents from a web search engine.
        :param prompt_node: The PromptNode used for generating the answer based on retrieved documents.
        """

        self.pipeline = Pipeline()
        self.pipeline.add_node(
            component=web_retriever, name="Retriever", inputs=["Query"]
        )

        self.pipeline.add_node(
            component=TopPSampler(top_p=0.95), name="Sampler", inputs=["Retriever"]
        )

        shaper = Shaper(
            func="top_3_documents",
            inputs={"documents": "documents"},
            outputs=["documents"],
        )
        self.pipeline.add_node(component=shaper, name="Shaper", inputs=["Sampler"])

        prompt_node = PromptNode(
            "gpt-3.5-turbo",
            api_key=Config["OPENAI_API_KEY"],
            max_length=Config["OPENAI_MAX_TOKENS_RESPONSE"],
            default_prompt_template=PromptTemplate(
                name="custom-question-answering-with-references",
                prompt_text="Create an informative answer (approximately 100 words) for a given question encased in citatations"
                "Either quote directly or summarize. If you summarize, adopt the tone of the source material. If either case, provide citations for every piece of information you include in the answer."
                "Always cite your sources, even if they do not directly answer the question.\n"
                "If the documents do not contain the answer to the question, provide a summary of the relevant information you find instead.\n\n"
                "Here are some examples:\n"
                "<https://example1.com|The Eiffel Tower is located in Paris>.'\n"
                "Question: Where is the Eiffel Tower located?; Answer: <https://example1.com|The Eiffel Tower is located in Paris>.\n"
                "<https://example2a.com|Python is a high-level programming language>.'\n"
                "<https://example2b.com|Python is a scripting language>.'\n"
                "Question: What is Python?; Answer: <https://example2a.com|Python is a high-level programming language>. <https://example2b.com|Python is a scripting language> \n\n"
                "Now, it's your turn.\n"
                "{join(documents, delimiter=new_line, pattern=new_line+'<$url|$content>', str_replace={new_line: ' ', '[': '(', ']': ')'})} \n Question: {query}; Answer: ",
                output_parser=AnswerParser(
                    reference_pattern=r"<(https?://[^|]+)\|[^>]+>"
                ),
            ),
            model_kwargs={"temperature": 0.2},
        )
        self.pipeline.add_node(
            component=prompt_node, name="PromptNode", inputs=["Shaper"]
        )

        self.metrics_filter = {"Retriever": ["recall_single_hit"]}

    def run(
        self, query: str, params: Optional[dict] = None, debug: Optional[bool] = None
    ):
        """
        :param query: The search query string.
        :param params: Params for the `Retriever`, `Sampler`, `Shaper`, and ``PromptNode. For instance,
                       params={"Retriever": {"top_k": 3}, "Sampler": {"top_p": 0.8}}. See the API documentation of each node for available parameters and their descriptions.
        :param debug: Whether the pipeline should instruct nodes to collect debug information
                      about their execution. By default, these include the input parameters
                      they received and the output they generated.
                      YOu can then find all debug information in the dict thia method returns
                      under the key "_debug".
        """
        output = self.pipeline.run(query=query, params=params, debug=debug)
        # Extract the answer from the last line of the PromptNode's output
        logger.debug(f"output: {output}")
        return output


web_qa_tool = Tool(
    name="Search",
    pipeline_or_node=CustomWebQAPipeline(),
    description="useful for when you need to Google questions.",
    output_variable="answers",
)
