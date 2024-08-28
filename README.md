# fragment-python

```python
from .fragment.sdk.client import Client

graphql_client = Client(
    client_id="<client id from the dashboard>",
    client_secret="<client secret from the dashboard>",
    api_url="<api url from the dashboard>",
    auth_url="<auth url from the dashboard>",
    auth_scope="<auth scope from the dashboard>",
  )

get_schema_result = await graphql_client.get_schema('<Your Schema Key here>')

# Prints out your Schema JSON
print(get_schema_result.schema_.json())
```

## Prerequisites

Install the SDK dependencies:
```shell
poetry install
```

Install the [Fragment CLI](https://github.com/fragment-dev/workspaces/pull/2143):

```shell
brew tap fragment-dev/tap &&\
  brew install fragment-dev/tap/fragment-cli
```

## Generate a GraphQL client

1. Download your Schema by running `fragment get-schema --key=<schema-key>`. This will write a .jsonc file to your CWD.
2. Generate the schema-based GraphQL queries by running `fragment gen-graphql --path=<path-to-schema.jsonc> --output=queries/schema_queries.graphql`. The `queries` folder exists within this repository already.
3. Run `poetry run gen-graphql` from the root of this project.
