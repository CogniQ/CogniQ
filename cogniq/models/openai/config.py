import os
Config = {
    "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
    "OPENAI_API_TYPE": os.environ.get("OPENAI_API_TYPE"),  # Azure
    "OPENAI_API_BASE": os.environ.get("OPENAI_API_BASE"),  # Azure
    "OPENAI_API_VERSION": os.environ.get("OPENAI_API_VERSION"),  # Azure
    "OPENAI_CHAT_MODEL": os.environ.get("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
    "OPENAI_EMBEDDING_MODEL": os.environ.get(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
    ),
    "OPENAI_TEXT_EMBEDDING_CHUNK_SIE": os.environ.get(
        "OPENAI_TEXT_EMBEDDING_CHUNK_SIE", 500
    ),
}
