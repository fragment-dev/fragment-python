from typing import Optional


class MissingTokenException(ValueError):
    """Token not found."""

    def __init__(self) -> None:
        super().__init__("Token is None")


class MissingArgumentException(ValueError):
    """Argument not present."""

    def __init__(self, argument: str) -> None:
        super().__init__(f"{argument} must be provided")


class TokenRequestException(Exception):
    """The auth endpoint did not return an access token."""

    def __init__(self, error: str, description: Optional[str] = None) -> None:
        self.error = error
        self.description = description
        super().__init__(f"{error}: {description}" if description else error)
