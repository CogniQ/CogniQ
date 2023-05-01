from cogniq.logging import setup_logger

logger = setup_logger(__name__)


def register_app_home_opened(*, app):
    @app.event("app_home_opened")
    async def update_home_tab(client, event):
        try:
            # views.publish is the method that your app uses to push a view to the Home tab
            await client.views_publish(
                # the user that opened your app's app home
                user_id=event["user"],
                # the view object that appears in the app home
                view={
                    "type": "home",
                    "callback_id": "home_view",
                    # body of the view
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Welcome to your _App's Home_* :tada:",
                            },
                        },
                        {"type": "divider"},
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app.",
                            },
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "Click me!"},
                                }
                            ],
                        },
                    ],
                },
            )

        except Exception as e:
            logger.error(f"Error publishing home tab: {e}")
