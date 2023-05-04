import os

Config = {
    "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
    "OPENAI_API_TYPE": os.environ.get("OPENAI_API_TYPE"),  # Azure
    "OPENAI_API_BASE": os.environ.get("OPENAI_API_BASE"),  # Azure
    "OPENAI_API_VERSION": os.environ.get("OPENAI_API_VERSION"),  # Azure
    "OPENAI_CHAT_MODEL": os.environ.get("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
    "OPENAI_MAX_TOKENS_HISTORY": os.environ.get("OPENAI_MAX_TOKENS_HISTORY", 800),
    "OPENAI_MAX_TOKENS_RETRIEVAL": os.environ.get("OPENAI_MAX_TOKENS_RETRIEVAL", 700),
    "OPENAI_MAX_TOKENS_PROMPT": os.environ.get("OPENAI_MAX_TOKENS_PROMPT", 1000),
    "OPENAI_MAX_TOKENS_RESPONSE": os.environ.get("OPENAI_MAX_TOKENS_RESPONSE", 800),
}
