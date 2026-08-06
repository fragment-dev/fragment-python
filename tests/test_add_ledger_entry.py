from uuid import uuid4

import pytest

from fragment.sdk.add_ledger_entry import (
    AddLedgerEntryAddLedgerEntryAddLedgerEntryResult,
)
from fragment.sdk.client import Client
from fragment.sdk.enums import CurrencyCode, CurrencyMode, LedgerAccountTypes
from fragment.sdk.input_types import (
    ChartOfAccountsInput,
    CreateLedgerInput,
    SchemaCurrencyMatchInput,
    SchemaInput,
    SchemaLedgerAccountInput,
    SchemaLedgerAccountMatchInput,
    SchemaLedgerEntriesInput,
    SchemaLedgerEntryInput,
    SchemaLedgerLineInput,
)

pytestmark = pytest.mark.integration

ENTRY_TYPE = "user-funds-account"


def build_schema(key: str) -> SchemaInput:
    """A minimal Schema: two root accounts and one templated Ledger Entry type."""
    usd = SchemaCurrencyMatchInput(code=CurrencyCode.USD)
    return SchemaInput(
        key=key,
        name="Add Ledger Entry Test Schema",
        chartOfAccounts=ChartOfAccountsInput(
            defaultCurrencyMode=CurrencyMode.multi,
            accounts=[
                SchemaLedgerAccountInput(
                    key="asset-root",
                    name="Asset Root",
                    type=LedgerAccountTypes.asset,
                    children=[],
                ),
                SchemaLedgerAccountInput(
                    key="liability-root",
                    name="Liability Root",
                    type=LedgerAccountTypes.liability,
                    children=[],
                ),
            ],
        ),
        ledgerEntries=SchemaLedgerEntriesInput(
            types=[
                SchemaLedgerEntryInput(
                    type=ENTRY_TYPE,
                    lines=[
                        SchemaLedgerLineInput(
                            key="asset-line",
                            account=SchemaLedgerAccountMatchInput(path="asset-root"),
                            amount="{{amount}}",
                            currency=usd,
                        ),
                        SchemaLedgerLineInput(
                            key="liability-line",
                            account=SchemaLedgerAccountMatchInput(
                                path="liability-root"
                            ),
                            amount="{{amount}}",
                            currency=usd,
                        ),
                    ],
                )
            ]
        ),
    )


@pytest.mark.asyncio
async def test_add_ledger_entry(client: Client) -> None:
    schema_key = str(uuid4())
    store_schema_response = await client.store_schema(schema=build_schema(schema_key))
    assert store_schema_response.store_schema.typename__ == "StoreSchemaResult"

    ledger_ik = str(uuid4())
    create_ledger_response = await client.create_ledger(
        ik=ledger_ik,
        ledger=CreateLedgerInput(name="Add Ledger Entry Test Ledger"),
        schema_key=schema_key,
    )
    assert create_ledger_response.create_ledger.typename__ == "CreateLedgerResult"

    entry_ik = str(uuid4())
    add_entry_response = await client.add_ledger_entry(
        ik=entry_ik,
        ledger_ik=ledger_ik,
        type_=ENTRY_TYPE,
        posted="1968-01-01T16:45:00Z",
        parameters=dict(amount="100"),
    )

    result = add_entry_response.add_ledger_entry
    assert isinstance(result, AddLedgerEntryAddLedgerEntryAddLedgerEntryResult)
    assert result.is_ik_replay is False
    assert result.entry.ik == entry_ik
    assert result.entry.type_ == ENTRY_TYPE

    amounts_by_path = {line.account.path: line.amount for line in result.lines}
    assert amounts_by_path == {"asset-root": "100", "liability-root": "100"}

    # Posting the same IK again is a replay of the original entry, not a new one.
    replay_response = await client.add_ledger_entry(
        ik=entry_ik,
        ledger_ik=ledger_ik,
        type_=ENTRY_TYPE,
        posted="1968-01-01T16:45:00Z",
        parameters=dict(amount="100"),
    )
    replay = replay_response.add_ledger_entry
    assert isinstance(replay, AddLedgerEntryAddLedgerEntryAddLedgerEntryResult)
    assert replay.is_ik_replay is True
    assert replay.entry.id == result.entry.id
