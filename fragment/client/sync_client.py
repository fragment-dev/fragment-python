# Ignore untyped authlib
# mypy: disable-error-code="import-untyped"
import time
from typing import Any, Dict, Optional

import httpx
from ariadne_codegen.client_generators.dependencies.base_client import BaseClient
from authlib.integrations.httpx_client import OAuth2Client

from fragment.exceptions import MissingArgumentException, MissingTokenException


class SyncFragmentClient(BaseClient):
    def __init__(
        self,
        api_url: str = "",
        auth_url: str = "",
        auth_scope: str = "",
        client_id: str = "",
        client_secret: str = "",
        http_client: Optional[httpx.Client] = None,
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
        self.oauth2_client = OAuth2Client(client_id, client_secret, scope=auth_scope)

    def refresh_token(self):
        now = time.time()
        if self.expiration_time is None or self.expiration_time <= now:
            self.token = self.oauth2_client.fetch_token(self.auth_url)
            self.expiration_time = now + self.token["expires_in"]

    def execute(
        self,
        query: str,
        operation_name: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        self.refresh_token()
        if self.token is None:
            raise MissingTokenException()
        headers = kwargs.get("headers", {})
        kwargs.update(
            headers={
                "Authorization": f'Bearer {self.token["access_token"]}',
                **headers,
            }
        )
        return super().execute(query, operation_name, variables, **kwargs)
