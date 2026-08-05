"""Integration tests for the `addLedgerEntries` batch mutation.

Stores the vendored template Schema, creates a Ledger against it, and posts a
batch of mixed entry types using the typed payloads generated in
`tests/snapshots/001-marketing-schema`. Exercising the snapshotted client means
these tests cover the code a customer actually gets, rather than a hand-written
approximation of it.

Requires live credentials; see tests/conftest.py.
"""

import json
from pathlib import Path
from typing import AsyncIterator, Dict
from uuid import uuid4

import pytest
import pytest_asyncio

# `sdk` is the snapshotted client, on sys.path via the `pythonpath` setting in
# pyproject.toml. Regenerate it with `make snapshots`.
from sdk.add_ledger_entries import (
    AddLedgerEntriesAddLedgerEntriesAddLedgerEntriesResult,
    AddLedgerEntriesAddLedgerEntriesBadRequestError,
)
from sdk.client import Client
from sdk.enums import CurrencyCode
from sdk.input_types import (
    AddLedgerEntryInput,
    CreateLedgerInput,
    LedgerEntryInput,
    LedgerMatchInput,
    SchemaInput,
)
from sdk.typed_entries import CardSettleV1, OrderPlacedV1

TEMPLATE_SCHEMA = Path(__file__).parent / "template-schema" / "schema.json"
UNKNOWN_ENTRY_TYPE = "not-in-this-schema"

# The Schema declares `currency` as a templated `String`, so the generated
# payloads annotate it `str` rather than `CurrencyCode`. Passing the generated
# enum anyway keeps the code typo-proof; because it subclasses `str`, pydantic
# coerces it to the plain `"USD"` and the wire payload is unchanged.
CURRENCY = CurrencyCode.USD

# `addLedgerEntries` is gated behind this header. Passed per call rather than
# baked into the client, so the SDK stays free of experiment-specific behaviour.
EXPERIMENTAL_HEADERS = {"X-Fragment-Experimental": "true"}


@pytest_asyncio.fixture
async def snapshot_client(credentials: Dict[str, str]) -> AsyncIterator[Client]:
    """A client built from the snapshotted SDK, not from `fragment.sdk`.

    Credentials are passed explicitly rather than as `**credentials` so the call
    typechecks -- `Client` also takes an `http_client`, which a `Dict[str, str]`
    cannot satisfy.
    """
    async with Client(
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        auth_scope=credentials["auth_scope"],
        auth_url=credentials["auth_url"],
        api_url=credentials["api_url"],
    ) as client:
        yield client


def load_template_schema(key: str) -> SchemaInput:
    """The vendored template Schema, re-keyed so each run gets its own."""
    raw = json.loads(TEMPLATE_SCHEMA.read_text())
    raw["key"] = key
    raw["name"] = key
    return SchemaInput.model_validate(raw)


async def setup_ledger(client: Client) -> str:
    """Store the template Schema, create a Ledger on it, return the Ledger IK."""
    schema_key = str(uuid4())
    stored = await client.store_schema(schema=load_template_schema(schema_key))
    assert stored.store_schema.typename__ == "StoreSchemaResult"

    ledger_ik = str(uuid4())
    created = await client.create_ledger(
        ik=ledger_ik,
        ledger=CreateLedgerInput(name="Batch Ledger Entries Test Ledger"),
        schema_key=schema_key,
    )
    assert created.create_ledger.typename__ == "CreateLedgerResult"
    return ledger_ik


@pytest.mark.asyncio
async def test_add_ledger_entries(snapshot_client: Client) -> None:
    """A batch of two different typed entry types commits, in input order."""
    ledger_ik = await setup_ledger(snapshot_client)
    user_id, order_id = str(uuid4()), str(uuid4())
    order_ik, settle_ik = str(uuid4()), str(uuid4())

    response = await snapshot_client.add_ledger_entries(
        entries=[
            OrderPlacedV1(
                ik=order_ik,
                ledger_ik=ledger_ik,
                user_id=user_id,
                order_id=order_id,
                order_cost="1000",
                currency=CURRENCY,
                platform_fee="100",
                driver_fee="200",
                restaurant_id=str(uuid4()),
                driver_id=str(uuid4()),
            ),
            # The user owes 1300 across cost and fees; settle it in the same batch.
            CardSettleV1(
                ik=settle_ik,
                ledger_ik=ledger_ik,
                user_id=user_id,
                order_id=order_id,
                currency=CURRENCY,
                amount="1300",
            ),
        ],
        headers=EXPERIMENTAL_HEADERS,
    )

    result = response.add_ledger_entries
    assert isinstance(result, AddLedgerEntriesAddLedgerEntriesAddLedgerEntriesResult)
    order, settle = result.results
    assert (order.entry.ik, order.entry.type_) == (order_ik, "order_placed")
    assert (settle.entry.ik, settle.entry.type_) == (settle_ik, "card_settle")

    cash_lines = [line for line in settle.lines if line.account.path == "assets/cash"]
    assert [line.amount for line in cash_lines] == ["1300"]


@pytest.mark.asyncio
async def test_add_ledger_entries_rejects_unknown_entry_type(
    snapshot_client: Client,
) -> None:
    """An entry type absent from the Schema rejects the batch.

    The bad entry is a raw `AddLedgerEntryInput` because a typed payload cannot
    express an entry type the Schema does not define -- which incidentally covers
    mixing raw and typed entries in one call.
    """
    ledger_ik = await setup_ledger(snapshot_client)

    response = await snapshot_client.add_ledger_entries(
        entries=[
            CardSettleV1(
                ik=str(uuid4()),
                ledger_ik=ledger_ik,
                user_id=str(uuid4()),
                order_id=str(uuid4()),
                currency=CURRENCY,
                amount="100",
            ),
            AddLedgerEntryInput(
                ik=str(uuid4()),
                entry=LedgerEntryInput(
                    ledger=LedgerMatchInput(ik=ledger_ik),
                    type=UNKNOWN_ENTRY_TYPE,
                    parameters=dict(amount="100"),
                ),
            ),
        ],
        headers=EXPERIMENTAL_HEADERS,
    )

    error = response.add_ledger_entries
    assert isinstance(error, AddLedgerEntriesAddLedgerEntriesBadRequestError)
    assert error.code
    assert error.message
