from datetime import datetime
from datetime import timezone
import textwrap


schedule_future_message_function = {
    "name": "schedule_future_message",
    "description": textwrap.dedent(
        f"""
        Sends a message at a specified time in the future.
        I specify the 'when_time' property to indicate a specific time to send the 'future_message'.
        I also specify the response to the user in the 'confirmation_response' property.
        The current time is {datetime.now(tz=timezone.utc).isoformat(timespec="minutes")}.
    """
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "confirmation_response": {
                "type": "string",
                "description": "The response to the query when a message has been scheduled.",
            },
            "future_message": {
                "type": "string",
                "description": "The message to send in the future.",
            },
            "when_time": {
                "type": "string",
                "description": "This is when the message is to be sent at a specific time. The time should be specified in ISO 8601 full-date 'T' full-time format in the UTC timezone(YYYY-MM-DDThh:mm:ssZ). The current time is %s"
                % datetime.now(tz=timezone.utc).isoformat(timespec="minutes"),
                "format": "date-time",
            },
        },
        "required": ["confirmation_response", "future_message", "when_time"],
    },
}
