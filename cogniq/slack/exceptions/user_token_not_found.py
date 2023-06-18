class UserTokenNotFound(Exception):
    """Exception raised when the user token cannot be found."""

    def __init__(self, *, user_id, message="User token not found"):
        self.user_id = user_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} for user ID: {self.user_id}"
