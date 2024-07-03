from .fragment_graphql_client import Client
from pydantic import BaseModel
from requests_oauth2client import OAuth2Client

class AccessToken(BaseModel):
    access_token: str
    expires_in: int

def get_access_token(
        token_endpoint: str,
        client_id: str,
        client_secret: str,
        scope: str,
):
    oauth2_client = OAuth2Client(token_endpoint, client_id=client_id, client_secret=client_secret)
    response = oauth2_client.client_credentials(scope=scope)
    return AccessToken(access_token=response.access_token, expires_in=response.expires_in)

def get_client(url: str, access_token: AccessToken):
    return Client(url, headers={'Authorization': f'Bearer {access_token.access_token}'})