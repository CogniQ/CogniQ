from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import json

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from cogniq.config import PERPLEXITY_API_KEY
from cogniq.openai import CogniqOpenAI


class CogniqPerplexity(CogniqOpenAI):
    CHAT_COMPLETIONS_URL = "https://api.perplexity.ai/chat/completions"
    COMPLETIONS_URL = "https://notimplemented.example.com/"
    API_KEY = PERPLEXITY_API_KEY

    async def async_completion_create(self, *, prompt: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError
