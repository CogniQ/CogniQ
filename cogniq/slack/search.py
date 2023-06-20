from typing import Callable

import logging

logger = logging.getLogger(__name__)

from slack_sdk.errors import SlackApiError


class Search:
    def __init__(self, *, cslack):
        """
        Search personality
        Please call async_setup after initializing the personality.

        ```
        search = Search(cslack=cslack)
        await search.async_setup()
        ```

        Parameters:
        cslack (CogniqSlack): CogniqSlack instance.
        """
        self.client = cslack.app.client
        self.installation_store = cslack.installation_store

    async def async_setup(self):
        """
        Please call after initializing the personality.
        """
        pass

    async def search_texts(self, *, q: str, context: Dict, filter: Callable = None, **kwargs) -> list[str]:
        """
        Search slack and format the response.

        Parameters:
        q: Query string to search.
        context: Context of the message from slack
        filter: Filter function to filter the messages.
                The function should return True if the message should be filtered out.
                If unset, all messages will be returned.
        kwargs: Additional parameters for the search.

        Returns:
        list: List of formatted messages.
        """
        messages = await self.search(q=q, context=context, **kwargs)

        if filter is None:
            filter = lambda message: True

        str_messages = []
        for message in messages:
            if filter(message):
                continue
            username = message["username"]
            text = message["text"]
            channel = message["channel"]["name"]
            permalink = message["permalink"]
            str_messages.append(f"<{permalink}|channel: {channel}, username: {username}, text: {text}>")

        return str_messages

    async def search(self, *, q: str, context: Dict, **kwargs) -> list[dict]:
        """
        Search slack and return the messages.

        Parameters:
        q (str): Query string to search.
        kwargs: Additional parameters for the search.

        Returns:
        list: List of messages.
        """
        response = await self._search(q=q, context=context, **kwargs)
        return response["messages"]["matches"]

    async def _search(self, *, q: str, context: Dict, **kwargs) -> dict:
        """
        Private method to perform the actual slack search.

        Parameters:
        q (str): Query string to search.
        kwargs: Additional parameters for the search.

        Returns:
        list: List of messages.

        Raises:
        SlackApiError: If an error occurs while performing the search.
        """
        default_parameters = {
            "sort": "timestamp",
            "sort_dir": "desc",
            "count": 40,
            "cursor": "*",
        }

        # Merge default_parameters and kwargs, with kwargs taking precedence
        search_parameters = {**default_parameters, **kwargs}
        user_token = context.get("user_token")  # or await self.installation_store.async_find_user_token(context=context)

        try:
            logger.info(f"Searching slack for {q}")
            team_id = context["team_id"]
            response = await self.client.search_messages(query=q, team_id=team_id, token=user_token, **search_parameters)

        except SlackApiError as e:
            if e.response["error"] == "not_allowed_token_type":
                error_string = f"""\
                             The token doesn't have the right permissions.
                             The search:read scope is required to call the search.messages method.
                             If you're using a user token or an app-level token, make sure your app has been granted this scope.
                             {e}
                             """
                logger.error(error_string)
                # I want to return the error string to the evaluator.
                error_message = {
                    "messages": {
                        "matches": [
                            {
                                "username": "SlackApiError",
                                "channel": {"name": "N/A"},
                                "text": error_string,
                            }
                        ]
                    }
                }
                return error_message
            else:
                raise e

        if response["ok"]:
            return response
        else:
            raise Exception(response["error"])
