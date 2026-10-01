"""OAuth2 client-credentials token request against the Fragment auth endpoint.

The SDK needs exactly one OAuth2 call: exchange a client ID and secret for an
access token. That is a single form POST, so it is made with httpx directly
rather than through an OAuth library, whose much larger surface (JOSE, OIDC,
server-side grants) customers would otherwise inherit, along with its
advisories.

The request matches what authlib's httpx `OAuth2Client.fetch_token` sent:
HTTP Basic client authentication (`client_secret_basic`) and a form body of
`grant_type=client_credentials` and `scope`.
"""

from typing import Any, Dict

import httpx

from fragment.exceptions import TokenRequestException

_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
}


def _token_request_kwargs(
    client_id: str, client_secret: str, scope: str
) -> Dict[str, Any]:
    return dict(
        data={"grant_type": "client_credentials", "scope": scope},
        auth=httpx.BasicAuth(client_id, client_secret),
        headers=_HEADERS,
    )


def _parse_token_response(response: httpx.Response) -> Dict[str, Any]:
    if response.status_code >= 500:
        response.raise_for_status()
    try:
        token = response.json()
    except ValueError as e:
        raise TokenRequestException(
            f"token endpoint returned a non-JSON response "
            f"(HTTP {response.status_code})"
        ) from e
    if not isinstance(token, dict):
        raise TokenRequestException("token endpoint returned a non-object response")
    if "error" in token:
        raise TokenRequestException(token["error"], token.get("error_description"))
    if "access_token" not in token or "expires_in" not in token:
        raise TokenRequestException(
            f"token endpoint response is missing access_token or expires_in "
            f"(HTTP {response.status_code})"
        )
    return token


def fetch_token(
    auth_url: str, client_id: str, client_secret: str, scope: str
) -> Dict[str, Any]:
    with httpx.Client() as client:
        response = client.post(
            auth_url, **_token_request_kwargs(client_id, client_secret, scope)
        )
    return _parse_token_response(response)


async def fetch_token_async(
    auth_url: str, client_id: str, client_secret: str, scope: str
) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            auth_url, **_token_request_kwargs(client_id, client_secret, scope)
        )
    return _parse_token_response(response)
