def register_app_mention(*, app, logger):
    @app.event("app_mention")
    def event_test(event, say):
        original_ts = event["ts"]
        say(f"You rang? <@{event['user']}>!", thread_ts=original_ts)
