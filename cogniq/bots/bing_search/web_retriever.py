from haystack.nodes.retriever.web import WebRetriever
from haystack.nodes.preprocessor import PreProcessor


def get_web_retriever(config: dict):
    return WebRetriever(
        api_key=config["BING_SUBSCRIPTION_KEY"],
        search_engine_provider="BingAPI",
        top_k=3,
        mode="preprocessed_documents",
        preprocessor=PreProcessor(progress_bar=False),
    )
