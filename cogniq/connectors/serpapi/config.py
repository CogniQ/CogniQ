import os

from serpapi import GoogleSearch

Config = {
    "SERPAPI_API_KEY": os.environ.get("SERPAPI_API_KEY"),
}

GoogleSearch.SERP_API_KEY = Config["SERPAPI_API_KEY"]
