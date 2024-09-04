# fragment-python

[Fragment](https://fragment.dev/) is the Ledger API for engineers that move money. Stop wrangling payment tables, debugging balance errors, and hacking together data pipelines. Start shipping the features that make a difference.

## Installation

Using `pip`:

```bash
pip install fragment-python
```

Using `poetry`:

```bash
poetry add fragment-python
```

## Usage

Get started by instantiating a `Client` from `fragment.sdk.client`. You can generate credentials using the Fragment [dashboard](https://dashboard.fragment.dev/go/s/api-clients)

```python
from fragment.sdk.client import Client

graphql_client = Client(
    client_id="<client id from the dashboard>",
    client_secret="<client secret from the dashboard>",
    api_url="<api url from the dashboard>",
    auth_url="<auth url from the dashboard>",
    auth_scope="<auth scope from the dashboard>",
  )

async def print_schema():
  get_schema_result = await graphql_client.get_schema("<Your schema key here>")
  print(get_schema_result.schema_.json())

import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(print_schema())
```

Read the [Using custom queries](#using-custom-queries) section to learn how to use your own GraphQL queries with the SDK.

### Using a synchronous client

If you prefer using a synchronous client instead of an async one, then:

```python
from fragment.sync_sdk.client import Client

graphql_client = Client(
    client_id="<client id from the dashboard>",
    client_secret="<client secret from the dashboard>",
    api_url="<api url from the dashboard>",
    auth_url="<auth url from the dashboard>",
    auth_scope="<auth scope from the dashboard>",
  )

get_schema_result = graphql_client.get_schema("<Your schema key here>")
print(get_schema_result.schema_.json())

```

## Examples

### Post a Ledger Entry

To [post](https://fragment.dev/docs#post-ledger-entries-post-to-the-api) a Ledger Entry defined in your Schema:

```python
await graphql_client.add_ledger_entry(
  ik="some-ik",
  ledger_ik="your-ledger-ik",
  type="user_funds_account",
  posted="1968-01-01T16:45:00Z",
  parameters=dict(
    user_id="user-1",
    funding_amount="20000",
  )
)
```

### Read a Ledger Account's Balance

To read a Ledger Account's [balance](https://fragment.dev/docs#read-balances-latest):

```python
from fragment.sdk.enums import CurrencyCode
from fragment.sdk.input_types import CurrencyMatchInput

await graphql_client.get_ledger_account_balance(
  ledger_ik="your-ledger-ik",
  path="liabilities/user:user-1/available",
  balance_currency=CurrencyMatchInput(code=CurrencyCode.USD),
)
```

## Using custom queries

While the SDK comes with GraphQL queries out of the box, you may want to customize these queries for your product. In order to do that:

1. Define your custom GraphQL queries in a GraphQL file. For example, in `queries/custom-queries.graphql`:
```graphql
query getSchemaName($key: SafeString!) {
  schema(schema: { key: $key }) {
    key
    name
  }
}
```
2. Run `fragment-python-client-codegen` to generate the GraphQL SDK client. GraphQL named queries are converted to snake_case to conform to Python's code conventions. Optionally, pass the `--sync` flag to generate a synchronous client instead of the default async GraphQL client.
```bash
fragment-python-client-codegen \
  --input-dir libs/fragment/queries/ \
  --target-package-name=custom_queries_package \
  --output-dir=libs/fragment
```
3. Use the client from the generated package in your product! Apart from the custom query methods, this client is functionally identical to `fragment.sdk.client.Client`

```python
from .libs.fragment.custom_queries_package.client import Client

graphql_client = Client(
    client_id="<client id from the dashboard>",
    client_secret="<client secret from the dashboard>",
    api_url="<api url from the dashboard>",
    auth_url="<auth url from the dashboard>",
    auth_scope="<auth scope from the dashboard>",
  )

async def print_schema_name():
  # Note that getSchemaName is converted to snake_case automatically
  response = await graphql_client.get_schema_name("<Your Schema Key>")
  print(response.schema_.key)

import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(print_schema())
```
