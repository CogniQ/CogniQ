from slack_bolt import App
from .config import Config
from .app_home_opened import register_app_home_opened
from .message import register_message 

app = App(
    token=Config["SLACK_BOT_TOKEN"],
    signing_secret=Config["SLACK_SIGNING_SECRET"],
)

register_app_home_opened(app)
register_message(app)

@app.event("app_mention")
def event_test(event, say):
    original_ts = event["ts"]
    say(f"Hi there, <@{event['user']}>!", thread_ts=original_ts)


def start():
    app.start(port=int(Config["PORT"]))