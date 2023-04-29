from cogniq.logging import setup_logger

from slack_bolt import App
from .config import Config
from .app_home_opened import register_app_home_opened
from .app_mention import register_app_mention
from .message import register_message

logger = setup_logger(__name__)

app = App(
    token=Config["SLACK_BOT_TOKEN"],
    signing_secret=Config["SLACK_SIGNING_SECRET"],
)

registration_config = {
    "app": app,
    "logger": logger,
}

register_app_home_opened(**registration_config)
register_app_mention(**registration_config)
register_message(**registration_config)

# Handle all non-registered events
@app.event("*")
def handle_all_events(body):
    logger.info(body)


def start():
    logger.info("Starting Slack app!!")
    app.start(port=int(Config["PORT"]))
 