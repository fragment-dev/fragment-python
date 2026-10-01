"""The client-credentials token request the SDK makes in place of authlib.

Offline: every request goes to an `httpx.MockTransport`.
"""

import base64
import json
from functools import partial
from typing import Any, Callable, List, TypedDict
from urllib.parse import parse_qs

import httpx
import pytest

from fragment.client import oauth
from fragment.client.async_client import AsyncFragmentClient
from fragment.client.sync_client import SyncFragmentClient
from fragment.exceptions import TokenRequestException

AUTH_URL = "https://auth.example.test/oauth2/token"
TOKEN = {"access_token": "tok", "expires_in": 3600, "token_type": "Bearer"}

Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture
def requests(monkeypatch: pytest.MonkeyPatch) -> List[httpx.Request]:
    """Route token requests to TOKEN and record them."""
    seen: List[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=TOKEN)

    route(monkeypatch, handler)
    return seen


def route(monkeypatch: pytest.MonkeyPatch, handler: Handler) -> None:
    transport = httpx.MockTransport(handler)
    sync_client = partial(httpx.Client, transport=transport)
    async_client = partial(httpx.AsyncClient, transport=transport)
    monkeypatch.setattr("fragment.client.oauth.httpx.Client", sync_client)
    monkeypatch.setattr("fragment.client.oauth.httpx.AsyncClient", async_client)


def respond(monkeypatch: pytest.MonkeyPatch, status: int, body: Any) -> None:
    content = body if isinstance(body, bytes) else json.dumps(body).encode()
    route(monkeypatch, lambda _: httpx.Response(status, content=content))


def test_sends_a_client_credentials_grant_with_basic_auth(
    requests: List[httpx.Request],
) -> None:
    assert oauth.fetch_token(AUTH_URL, "id", "secret", "scope-a") == TOKEN

    (request,) = requests
    assert request.method == "POST"
    assert str(request.url) == AUTH_URL
    expected = base64.b64encode(b"id:secret").decode()
    assert request.headers["Authorization"] == f"Basic {expected}"
    assert request.headers["Accept"] == "application/json"
    assert parse_qs(request.content.decode()) == {
        "grant_type": ["client_credentials"],
        "scope": ["scope-a"],
    }


@pytest.mark.asyncio
async def test_async_sends_the_same_request(requests: List[httpx.Request]) -> None:
    assert await oauth.fetch_token_async(AUTH_URL, "id", "secret", "s") == TOKEN
    (request,) = requests
    assert parse_qs(request.content.decode())["grant_type"] == ["client_credentials"]


def test_raises_the_oauth_error_from_the_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    respond(
        monkeypatch,
        400,
        {"error": "invalid_client", "error_description": "bad secret"},
    )
    with pytest.raises(TokenRequestException) as raised:
        oauth.fetch_token(AUTH_URL, "id", "secret", "s")
    assert raised.value.error == "invalid_client"
    assert raised.value.description == "bad secret"


def test_raises_on_a_server_error(monkeypatch: pytest.MonkeyPatch) -> None:
    respond(monkeypatch, 503, {})
    with pytest.raises(httpx.HTTPStatusError):
        oauth.fetch_token(AUTH_URL, "id", "secret", "s")


@pytest.mark.parametrize(
    "body",
    [b"<html>gateway</html>", [], {"access_token": "tok"}],
    ids=["not-json", "not-an-object", "missing-expires-in"],
)
def test_raises_when_the_response_is_not_a_token(
    monkeypatch: pytest.MonkeyPatch, body: Any
) -> None:
    respond(monkeypatch, 200, body)
    with pytest.raises(TokenRequestException):
        oauth.fetch_token(AUTH_URL, "id", "secret", "s")


class ClientKwargs(TypedDict):
    api_url: str
    auth_url: str
    auth_scope: str
    client_id: str
    client_secret: str


CLIENT_KWARGS: ClientKwargs = {
    "api_url": "https://api.example.test/graphql",
    "auth_url": AUTH_URL,
    "auth_scope": "s",
    "client_id": "id",
    "client_secret": "secret",
}


def test_sync_client_fetches_once_until_expiry(
    requests: List[httpx.Request],
) -> None:
    client = SyncFragmentClient(**CLIENT_KWARGS)
    client.refresh_token()
    client.refresh_token()
    assert client.token == TOKEN
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_async_client_fetches_once_until_expiry(
    requests: List[httpx.Request],
) -> None:
    client = AsyncFragmentClient(**CLIENT_KWARGS)
    await client.refresh_token()
    await client.refresh_token()
    assert client.token == TOKEN
    assert len(requests) == 1
