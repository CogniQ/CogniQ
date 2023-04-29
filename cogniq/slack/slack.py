from slack_bolt import App
from .config import Config
from .app_home_opened import register_app_home_opened
from .app_mention import register_app_mention
from .message import register_message 

app = App(
    token=Config["SLACK_BOT_TOKEN"],
    signing_secret=Config["SLACK_SIGNING_SECRET"],
)

register_app_home_opened(app)
register_app_mention(app)
register_message(app)



def start():
    app.start(port=int(Config["PORT"]))