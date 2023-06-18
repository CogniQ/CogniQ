def evaluator_prompt(responses_with_descriptions: list, q: str):
    """
    The evaluator prompt.
    """
    formatted_responses = "\n\n".join(
        f"Description of the Responder: {description}. Response: {response}" for description, response in responses_with_descriptions
    )
    return f"""\
    Given the Query, and considering the entirety of the following Responses, please synthesize <https://example.com/response-rules|the most appropriate, coherent, and comprehensive response>.
    Be advised that some of the Responses may be irrelevant, and that you should not use them in your response.
    <https://example.com/citation|Preserve any citations if they are relevant to the response>.
    You are designed to combine the strengths of Responders enabled with various information retrieval systems and produce the best possible response,
    so never mention or repeat that you are unable to perform web searches, access real time data, unable to predict future data etc..

    Note: If you receive any USER_NOTIFICATION messages, convey them verbatim to the user in your response.

    Query: {q}
    {formatted_responses}"""
