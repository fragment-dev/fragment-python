# fragment-python

```python
from .client import get_access_token, get_client

access_token = get_access_token(
  "<auth url from dashboard>", "<client id from dashboard>", "<client secret from dashboard>")

graphql_client = get_client("<api url from dashboard>", access_token)

get_schema_result = await graphql_client.get_schema('<Your Schema Key here>')

# Prints out your Schema JSON
print(get_schema_result.schema_.json())
```

## To generate a GraphQL client

1. Download your Schema by running `fragment get-schema --key=<schema-key>`. This will write a .jsonc file to your CWD.
2. Generate the schema-based GraphQL queries by running `fragment gen-graphql --path=<path-to-schema.jsonc> --output=queries/schema_queries.graphql`. The `queries` folder exists within this repository already.
3. Run `ariadne-codegen` from the root of this project.
