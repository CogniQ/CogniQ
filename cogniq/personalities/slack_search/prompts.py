from typing import *

from functools import singledispatch


@singledispatch
def formatted_responses(responses: list):
    """
    Format responses for the evaluator.
    """
    return "\n\n".join(responses)


@formatted_responses.register
def _(responses: str):
    return f"Slack Search Result Summary: {responses}"


def retrieval_augmented_prompt(slack_search_response: Union[list, str], q: str):
    """
    The prompt
    """
    return f"""\
    Given the Query, and considering the entirety of the following Slack Search Results, please remove the irrelevant results and return the remainder.

    Do not add any additional information to the response.
    
    Query: <###
        {q}
    ###>

    Slack Search Results: <###
    {formatted_responses(slack_search_response)}
    ###>

    Relevant Slack Search Results: <###"""
