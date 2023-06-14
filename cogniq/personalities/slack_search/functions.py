from datetime import date

get_search_query_function = {
    "name": "get_search_query",
    "description": "Get a slack keyword search query for the user's question.",
    "parameters": {
        "type": "object",
        "properties": {
            "phrases": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific phrases to search for, encapsulated in double quotes. Use '*' as a wildcard, for example when the user asks for a summary of a channel, thread, or time period. Required.",
            },
            "negative_words": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Omit results that contain these specific words. Optional, used to narrow search results.",
            },
            "in": {
                "type": "string",
                "description": "A channel name, display name, or section name to search within specific conversations. Optional, used to narrow search results.",
            },
            "from": {
                "type": "string",
                "description": "A display name to search for conversations with a specific person. Optional, used to narrow search results.",
            },
            "with": {
                "type": "string",
                "description": "A display name to search in threads and direct messages (DMs) with a specific person. Optional, used to narrow search results.",
            },
            "has": {
                "type": "string",
                "description": "A specific emoji to search for reactions. Use 'link' to search for messages with URLs. Use 'star' to search for messages that the user starred. Optional, used to narrow search results.",
            },
            "before": {
                "type": "string",
                "description": "A YYYY-MM-DD date to search before. Optional, used to narrow search results. Cannot be used with after, during, or on. Today is %s"
                % date.today(),
                "format": "date",
            },
            "after": {
                "type": "string",
                "description": "A YYYY-MM-DD date to search after. Optional, used to narrow search results. Cannot be used with before, during, or on. Today is %s"
                % date.today(),
                "format": "date",
            },
            "during": {
                "type": "string",
                "description": "A month or year to search during. Optional, used to narrow search results. Cannot be used with before, after, or on. Today is %s"
                % date.today(),
                "format": "date",
            },
            "on": {
                "type": "string",
                "description": "A specific day (YYYY-MM-DD) to search on. Optional, used to narrow search results. Cannot be used with before, after, or during. Today is %s"
                % date.today(),
                "format": "date",
            },
            "is_thread": {
                "type": "boolean",
                "description": "Exclusively search in threads. Optional, used to narrow search results.",
            },
        },
        "required": ["phrases"],
    },
}
