from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

from functools import singledispatch


@singledispatch
def formatted_responses(responses: Any) -> str:
    """
    Format responses for the evaluator.
    """
    raise NotImplementedError


@formatted_responses.register
def _(responses: list) -> str:
    """
    Format responses for the evaluator.
    """
    return "\n\n".join(responses)


@formatted_responses.register
def _(responses: str) -> str:
    return f"Slack Search Result Summary: {responses}"


def retrieval_augmented_prompt(slack_search_response: list | str, q: str) -> str:
    """
    The prompt
    """
    return f"""\
    Given the Query, and considering the entirety of the following Slack Search Results, please remove the irrelevant results and return the remainder.

    Do not add any additional information to the response.

    If Slack Search Results are missing. Return the following message: "No Slack Search Results"
    
    Example:
    Query: <###
        "How do I do X?"
    ###>

    Slack Search Results: <###
    ###>

    Relevant Slack Search Results: <###
        No Slack Search Results
    ###>

    Example:
    Query: <###
        "How do I do X?"
    ###>

    Slack Search Results: <###
        <https://cogniq.slack.com/archives/C01UZABCDEF/p1629788054000100|channel: general, username: @alice, text: How do I do X?>
        <https://cogniq.slack.com/archives/C01UZABCDEF/p1629788054000100|channel: general, username: @bob, text: You can do X by first asking @charlie.>
    ###>

    Relevant Slack Search Results: <###
        <https://cogniq.slack.com/archives/C01UZABCDEF/p1629788054000100|channel: general, username: @alice, text: How do I do X?>
        <https://cogniq.slack.com/archives/C01UZABCDEF/p1629788054000100|channel: general, username: @bob, text: You can do X by first asking @charlie.>
    ###>

    Now your turn:
    Query: <###
        {q}
    ###>

    Slack Search Results: <###
    {formatted_responses(slack_search_response)}
    ###>

    Relevant Slack Search Results: <###"""
