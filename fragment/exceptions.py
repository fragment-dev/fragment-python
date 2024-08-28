class MissingTokenException(ValueError):
    """Token not found."""

    def __init__(self):
        super().__init__("Token is None")


class MissingArgumentException(ValueError):
    """Argument not present."""

    def __init__(self, argument: str):
        super().__init__(f"{argument} must be provided")
