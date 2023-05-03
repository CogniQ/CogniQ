import os

Config = {
    "BING_SUBSCRIPTION_KEY": os.environ["BING_SUBSCRIPTION_KEY"],
    "BING_SEARCH_ENDPOINT": os.environ.get(
        "BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com"
    ),
}
