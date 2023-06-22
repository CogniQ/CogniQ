from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from .prompts import web_retriever_prompt

from haystack.pipelines import BaseStandardPipeline

from haystack.nodes.retriever.web import WebRetriever
from haystack.nodes import (
    PromptNode,
)
from haystack.pipelines.base import Pipeline
from haystack.nodes.retriever.web import WebRetriever
from haystack.nodes.preprocessor import PreProcessor

from typing import Optional


class CustomWebQAPipeline(BaseStandardPipeline):
    """
    Pipeline for Generative Question Answering performed based on Documents returned from a web search engine.
    """

    def __init__(self, *, config: Dict):
        """
        CustomWebQAPipeline constructor.

        Parameters:
        config (dict): Configuration for the pipeline with the following keys:
            OPENAI_API_KEY (str): OpenAI API key.
            OPENAI_MAX_TOKENS_RESPONSE (int): Maximum number of tokens in the response.
            BING_SUBSCRIPTION_KEY (str): Bing subscription key.
        """
        self.config = config

        self.web_retriever = WebRetriever(
            api_key=self.config["BING_SUBSCRIPTION_KEY"],
            search_engine_provider="BingAPI",
            top_k=5,
            mode="preprocessed_documents",
            preprocessor=PreProcessor(progress_bar=False),
        )

        self.pipeline = Pipeline()
        self.pipeline.add_node(component=self.web_retriever, name="Retriever", inputs=["Query"])

        prompt_node = PromptNode(
            "gpt-3.5-turbo",
            api_key=self.config["OPENAI_API_KEY"],
            max_length=self.config["OPENAI_MAX_TOKENS_RESPONSE"],
            default_prompt_template=web_retriever_prompt,
            model_kwargs={"temperature": 0.2},
        )
        self.pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

        self.metrics_filter = {"Retriever": ["recall_single_hit"]}

    def run(self, query: str, params: Dict | None = None, debug: bool | None = None):
        """
        :param query: The search query string.
        :param params: Params for the `Retriever`, `Sampler`, `Shaper`, and ``PromptNode. For instance,
                       params={"Retriever": {"top_k": 3}, "Sampler": {"top_p": 0.8}}. See the API documentation of each node for available parameters and their descriptions.
        :param debug: Whether the pipeline should instruct nodes to collect debug information
                      about their execution. By default, these include the input parameters
                      they received and the output they generated.
                      You can then find all debug information in the dict thia method returns
                      under the key "_debug".
        """
        output = self.pipeline.run(query=query, params=params, debug=debug)
        # Extract the answer from the last line of the PromptNode's output
        logger.debug(f"output: {output}")
        # logger.info(f"debug: {output['_debug']}")
        return output
