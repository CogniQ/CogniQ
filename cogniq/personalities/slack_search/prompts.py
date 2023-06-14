def retrieval_augmented_prompt(slack_search_response: list, q: str):
    """
    The prompt
    """
    formatted_responses = "\n\n".join(f"Slack Search Result: {response}" for response in slack_search_response)
    return f"""\
    Given the Query, and considering the entirety of the following Slack Search Results, please synthesize the most appropriate, coherent, and comprehensive response.
    Be advised that some of the Results may be irrelevant, and that you should not use them in your response.
    You are designed to combine the strengths of Responders enabled with various information retrieval systems and produce the best possible response,
    so never mention or repeat that you are unable to perform web searches, access real time data, unable to predict future data etc..
    
    Cite your sources, by using slack formatting. For example,
    In #general, @cogniq said "Hello, I am Cogniq. I am a slack bot that can answer your questions."

    Query: {q}
    {formatted_responses}
    Comprehensive Response:"""
