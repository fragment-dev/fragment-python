# Example Usage

```python
from .client import get_access_token, get_client

access_token = get_access_token(
  "<auth url from dashboard>", "<client id from dashboard>", "<client secret from dashboard>")

graphql_client = get_client("<api url from dashboard>", access_token)

get_schema_result = await graphql_client.get_schema('<Your Schema Key here>')

# Prints out your Schema JSON
print(get_schema_result.schema_.json())
```
