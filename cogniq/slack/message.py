def register_message(*, app, logger):
    @app.event("message")
    async def handle_message_events(event, say):
        original_ts = event["ts"]
        channel_type = event["channel_type"]
        user = event["user"]
        if channel_type == "im":
            await say(
                f"IM received from <@{user}>!",
            )
        elif channel_type == "mpim":
            await say(f"MPIM received from <@{user}>!", thread_ts=original_ts)
        elif channel_type == "channel":
            await say(
                f"Channel message received from <@{user}>!", thread_ts=original_ts
            )
        elif channel_type == "group":
            await say(f"Group message received from <@{user}>!", thread_ts=original_ts)
        else:
            await say(
                f"#{channel_type} received, <@{event['user']}>!", thread_ts=original_ts
            )
