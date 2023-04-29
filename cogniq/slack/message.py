def register_message(*, app, logger):
    @app.event("message")
    def handle_message_events(event, say):
        original_ts = event["ts"]
        channel_type = event["channel_type"]
        user = event["user"]
        if channel_type == "im":
            say(f"IM received from <@{user}>!",)
        elif channel_type == "mpim":
            say(f"MPIM received from <@{user}>!", thread_ts=original_ts)
        elif channel_type == "channel":
            say(f"Channel message received from <@{user}>!", thread_ts=original_ts)
        elif channel_type == "group":
            say(f"Group message received from <@{user}>!", thread_ts=original_ts)
        else:
            say(f"#{channel_type} received, <@{event['user']}>!", thread_ts=original_ts)
