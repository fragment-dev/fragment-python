"""Integration tests for the `addLedgerEntries` batch mutation.

Stores the vendored template Schema, creates a Ledger against it, and posts a
batch using the typed payloads generated in
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
    AddLedgerEntriesAddLedgerEntriesAddLedgerEntriesError,
    AddLedgerEntriesAddLedgerEntriesAddLedgerEntriesResult,
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
from sdk.typed_entries import OrderPlacedV1

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


def order_placed(
    ik: str, ledger_ik: str, user_id: str, order_cost: str, platform_fee: str
) -> OrderPlacedV1:
    """An `order_placed` payload; the ids that do not matter here are random."""
    return OrderPlacedV1(
        ik=ik,
        ledger_ik=ledger_ik,
        user_id=user_id,
        order_id=str(uuid4()),
        order_cost=order_cost,
        currency=CURRENCY,
        platform_fee=platform_fee,
        driver_fee="200",
        restaurant_id=str(uuid4()),
        driver_id=str(uuid4()),
    )


@pytest.mark.asyncio
async def test_add_ledger_entries(snapshot_client: Client) -> None:
    """A batch of two `order_placed` entries commits, in input order."""
    ledger_ik = await setup_ledger(snapshot_client)
    user_id = str(uuid4())
    first_ik, second_ik = str(uuid4()), str(uuid4())

    response = await snapshot_client.add_ledger_entries(
        entries=[
            order_placed(first_ik, ledger_ik, user_id, "1000", "100"),
            order_placed(second_ik, ledger_ik, user_id, "500", "50"),
        ],
        headers=EXPERIMENTAL_HEADERS,
    )

    result = response.add_ledger_entries
    assert isinstance(result, AddLedgerEntriesAddLedgerEntriesAddLedgerEntriesResult)
    first, second = result.results
    assert [first.entry.ik, second.entry.ik] == [first_ik, second_ik]
    assert {r.entry.type_ for r in result.results} == {"order_placed"}

    # Each entry books its own platform fee, so the amounts track the inputs.
    def platform_fee(committed) -> list:
        return [
            line.amount
            for line in committed.lines
            if line.account.path == "income/platform_fee"
        ]

    assert platform_fee(first) == ["100"]
    assert platform_fee(second) == ["50"]


@pytest.mark.asyncio
async def test_add_ledger_entries_rejects_unknown_entry_type(
    snapshot_client: Client,
) -> None:
    """An entry type absent from the Schema rejects the batch.

    Uses a raw `AddLedgerEntryInput` because a typed payload cannot express an
    entry type the Schema does not define.
    """
    ledger_ik = await setup_ledger(snapshot_client)

    response = await snapshot_client.add_ledger_entries(
        entries=[
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
    assert isinstance(error, AddLedgerEntriesAddLedgerEntriesAddLedgerEntriesError)
    assert error.code
    assert error.message
