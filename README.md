# fragment-python

[Fragment](https://fragment.dev/) is the Ledger API for engineers that move money. Stop wrangling payment tables, debugging balance errors, and hacking together data pipelines. Start shipping the features that make a difference.

See [CHANGELOG.md](CHANGELOG.md) for release notes and upgrade guidance.

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

### Post a batch of Ledger Entries

`add_ledger_entries` commits every entry in one atomic, strongly-consistent
transaction — either all of them are committed, or none are. It takes a list of
`AddLedgerEntryInput`:

```python
from fragment.sdk.input_types import (
    AddLedgerEntryInput,
    LedgerEntryInput,
    LedgerMatchInput,
)

await graphql_client.add_ledger_entries(
  entries=[
    AddLedgerEntryInput(
      ik="some-ik",
      entry=LedgerEntryInput(
        ledger=LedgerMatchInput(ik="your-ledger-ik"),
        type="user_funds_account",
        parameters=dict(user_id="user-1", funding_amount="20000"),
      ),
    ),
  ],
)
```

Because `parameters` is an untyped JSON field, nothing checks those parameter
names or values. See below for typed payloads that do.

### Strongly-typed batch payloads

A batch mutation takes one list of one input type, so GraphQL cannot type each
entry's `parameters` individually. The SDK closes that gap at codegen time: if
your codegen input directory contains the per-entry-type `addLedgerEntry`
operations for your Schema, a `typed_entries` module is generated alongside the
client with one model per entry type.

Given an operation like this in `queries/`:

```graphql
mutation PostAuthCapture(
  $ik: SafeString!
  $ledgerIk: SafeString!
  $user_id: String!
  $capture_amount: String!
) {
  addLedgerEntry(
    ik: $ik
    entry: {
      ledger: { ik: $ledgerIk }
      type: "auth_capture"
      parameters: { user_id: $user_id, capture_amount: $capture_amount }
    }
  ) {
    __typename
  }
}
```

you get an `AuthCaptureV1` model named for the entry type and version, and can build batch
payloads with real field names and types:

```python
from .libs.fragment.custom_queries_package.typed_entries import (
    AuthCaptureV1,
    PlatformFundsAccountV1,
)

await graphql_client.add_ledger_entries(
  entries=[
    AuthCaptureV1(
      ik="ik-1",
      ledger_ik="your-ledger-ik",
      user_id="user-1",
      capture_amount="100",
    ),
    PlatformFundsAccountV1(
      ik="ik-2",
      ledger_ik="your-ledger-ik",
      funding_amount="20000",
    ),
  ],
)
```

Typed entries can be mixed with raw `AddLedgerEntryInput` values in the same
call. Every model also accepts the optional `posted`, `tags`, `groups`, and
`conditions` fields, and exposes `to_input()` if you want the raw
`AddLedgerEntryInput` — for example to inspect or adjust a payload before
sending it. `to_entry_inputs()` converts a whole list at once.

Parameter names are preserved on the wire even when the Python field has to be
escaped: a parameter named `type`, `class`, or `json` becomes `type_`, `class_`,
or `json_` in Python but is still sent under its original Schema name.

Model names always carry the entry type's version, defaulting to `V1` when the
operation pins no `typeVersion`. This means adding a new version to your Schema
never renames an existing model, so it cannot break call sites. The default is
naming only — an unpinned `typeVersion` is still omitted from the request.

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
