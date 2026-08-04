import os
from typing import AsyncIterator, Dict

import pytest
import pytest_asyncio

from fragment.sdk.client import Client

REQUIRED_ENV_VARS = ("CLIENT_ID", "CLIENT_SECRET", "SCOPE", "AUTH_URL", "API_URL")


@pytest.fixture(scope="session")
def credentials() -> Dict[str, str]:
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
async def client(credentials: Dict[str, str]) -> AsyncIterator[Client]:
    async with Client(**credentials) as graphql_client:
        yield graphql_client
