def register_app_mention(app):
    @app.event("app_mention")
    def event_test(event, say):
        original_ts = event["ts"]
        say(f"Hi there, <@{event['user']}>!", thread_ts=original_ts)
