def register_message(app):
    @app.event("message")
    def handle_message_events(body, logger):
        logger.info(body)
