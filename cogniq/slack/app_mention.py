def register_app_mention(*, app, logger):
    @app.event("app_mention")
    async def event_test(event, say):
        original_ts = event["ts"]
        await say(f"You rang? <@{event['user']}>!", thread_ts=original_ts)
