def evaluator_prompt(responses: list, q: str):
    """
    The evaluator prompt.
    """
    return f"""\
    Given the Query, and considering the entirety of the following Responses, please synthesize the most appropriate, coherent, and comprehensive response.
    Be advised that some of the responses may be irrelevant, and that you should not use them in your response.
    Preserve any citations if they are relevant to the response.

    Query: {q}
    """ + '\n\nResponse: '.join(response for response in responses)
