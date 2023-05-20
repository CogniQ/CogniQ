from .config import Config

from haystack.nodes.retriever.web import WebRetriever
from haystack.nodes.preprocessor import PreProcessor


web_retriever = WebRetriever(
    api_key=Config["BING_SUBSCRIPTION_KEY"],
    search_engine_provider="BingAPI",
    top_k=3,
    mode="preprocessed_documents",
    preprocessor=PreProcessor(progress_bar=False),
)
