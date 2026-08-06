import os
from typing import AsyncIterator, TypedDict

import pytest
import pytest_asyncio

from fragment.sdk.client import Client

REQUIRED_ENV_VARS = ("CLIENT_ID", "CLIENT_SECRET", "SCOPE", "AUTH_URL", "API_URL")


class Credentials(TypedDict):
    """The `Client` keyword arguments read from the environment.

    A TypedDict rather than `Dict[str, str]` so `Client(**credentials)`
    typechecks: against a plain str mapping, a key could land on `http_client`,
    which takes an `AsyncClient`.
    """

    client_id: str
    client_secret: str
    auth_scope: str
    auth_url: str
    api_url: str


@pytest.fixture(scope="session")
def credentials() -> Credentials:
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        pytest.fail(
            "Integration tests need credentials from "
            "https://dashboard.fragment.dev/go/s/api-clients. "
            f"Missing environment variables: {', '.join(missing)}",
            pytrace=False,
        )
    return {
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "auth_scope": os.environ["SCOPE"],
        "auth_url": os.environ["AUTH_URL"],
        "api_url": os.environ["API_URL"],
    }


@pytest_asyncio.fixture
async def client(credentials: Credentials) -> AsyncIterator[Client]:
    async with Client(**credentials) as graphql_client:
        yield graphql_client
