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
        # self.user_token = cslack.config["SLACK_USER_TOKEN"]

    async def async_setup(self):
        """
        Please call after initializing the personality.
        """
        pass

    async def search_texts(self, *, q: str, context: dict, **kwargs) -> list:
        """
        Search slack and format the response.

        Parameters:
        q (str): Query string to search.
        kwargs: Additional parameters for the search.

        Returns:
        list: List of formatted messages.
        """
        messages = await self.search(q=q, context=context, **kwargs)

        str_messages = []
        for message in messages:
            username = message["username"]
            text = message["text"]
            channel = message["channel"]["name"]
            str_messages.append(f"channel: {channel}, username: {username}, text: {text}")

        return str_messages

    async def search(self, *, q: str, context: dict, **kwargs) -> list:
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

    async def _search(self, *, q: str, context: dict, **kwargs) -> list:
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
            "count": 20,
            "cursor": "*",
        }

        # Merge default_parameters and kwargs, with kwargs taking precedence
        search_parameters = {**default_parameters, **kwargs}

        try:
            logger.info(f"Searching slack for {q}")
            team_id = context["team_id"]
            user_token = context["user_token"]
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