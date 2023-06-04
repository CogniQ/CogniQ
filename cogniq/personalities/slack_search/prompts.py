def search_prompt(q: str):
    """
    The search prompt.
    """
    return f"""\
    Provide a Slack search query that will return the most relevant results for the following query.

    If more than one search term is provided, users and channels are also matched at a lower priority. To specifically search within a channel, group, or DM, add in:channel_name, in:group_name, or in:<@UserID>. To search for messages from a specific speaker, add from:<@UserID> or from:botname
    For IM results, the type is set to "im" and the channel.name property contains the user ID of the target user. For private group results, type is set to "group".

    
    {q}"""


def retrieval_augmented_prompt(slack_search_response: list, q: str):
    """
    The prompt
    """
    formatted_responses = "\n\n".join(
        f"Slack Search Result: {response}" for response in slack_search_response
    )
    return f"""\
    Given the Query, and considering the entirety of the following Slack Search Results, please synthesize the most appropriate, coherent, and comprehensive response.
    Be advised that some of the Results may be irrelevant, and that you should not use them in your response.
    You are designed to combine the strengths of Responders enabled with various information retrieval systems and produce the best possible response,
    so never mention or repeat that you are unable to perform web searches, access real time data, unable to predict future data etc..

    Query: {q}
    {formatted_responses}"""
