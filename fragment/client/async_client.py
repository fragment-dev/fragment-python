# Ignore untyped authlib
# mypy: disable-error-code="import-untyped"
import time
from typing import Any, Dict, Optional

import httpx
from ariadne_codegen.client_generators.dependencies.async_base_client import (
    AsyncBaseClient,
)
from authlib.integrations.httpx_client import AsyncOAuth2Client

from fragment.exceptions import MissingArgumentException, MissingTokenException


class AsyncFragmentClient(AsyncBaseClient):
    def __init__(
        self,
        api_url: str = "",
        auth_url: str = "",
        auth_scope: str = "",
        client_id: str = "",
        client_secret: str = "",
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        if api_url == "":
            raise MissingArgumentException("api_url")
        if auth_url == "":
            raise MissingArgumentException("auth_url")
        if auth_scope == "":
            raise MissingArgumentException("auth_scope")
        if client_id == "":
            raise MissingArgumentException("client_id")
        if client_secret == "":
            raise MissingArgumentException("client_secret")
        super().__init__(url=api_url, http_client=http_client)

        self.auth_url = auth_url
        self.expiration_time = None
        self.token = None
        self.oauth2_client = AsyncOAuth2Client(
            client_id, client_secret, scope=auth_scope
        )

    async def refresh_token(self):
        now = time.time()
        if self.expiration_time is None or self.expiration_time <= now:
            self.token = await self.oauth2_client.fetch_token(self.auth_url)
            self.expiration_time = now + self.token["expires_in"]

    async def execute(
        self,
        query: str,
        operation_name: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        await self.refresh_token()
        if self.token is None:
            raise MissingTokenException()
        headers = kwargs.get("headers", {})
        kwargs.update(
            headers={
                "Authorization": f'Bearer {self.token["access_token"]}',
                **headers,
            }
        )
        return await super().execute(query, operation_name, variables, **kwargs)
