# Generated by ariadne-codegen
# Source: schema.graphql

from typing import Any, List, Optional

from pydantic import Field

from .base_model import BaseModel
from .enums import (
    BalanceUpdateConsistencyMode,
    CurrencyCode,
    CurrencyMode,
    LedgerAccountTypes,
    LedgerLinesConsistencyMode,
    LedgerTypes,
    SceneEventType,
    SchemaConsistencyMode,
    TxType,
)


class ChartOfAccountsInput(BaseModel):
    accounts: List["SchemaLedgerAccountInput"]
    default_consistency_config: Optional["LedgerAccountConsistencyConfigInput"] = Field(
        alias="defaultConsistencyConfig", default=None
    )
    default_currency: Optional["CurrencyMatchInput"] = Field(
        alias="defaultCurrency", default=None
    )
    default_currency_mode: Optional[CurrencyMode] = Field(
        alias="defaultCurrencyMode", default=None
    )


class CreateCustomCurrencyInput(BaseModel):
    custom_code: str = Field(alias="customCode")
    custom_currency_id: Any = Field(alias="customCurrencyId")
    name: str
    precision: int


class CreateLedgerAccountInput(BaseModel):
    consistency_config: Optional["LedgerAccountConsistencyConfigInput"] = Field(
        alias="consistencyConfig", default=None
    )
    currency: Optional["CurrencyMatchInput"] = None
    currency_mode: Optional[CurrencyMode] = Field(alias="currencyMode", default=None)
    linked_account: Optional["ExternalAccountMatchInput"] = Field(
        alias="linkedAccount", default=None
    )
    name: str
    parent: Optional["LedgerAccountMatchInput"] = None
    type: Optional[LedgerAccountTypes] = None


class CreateLedgerAccountsInput(BaseModel):
    child_ledger_accounts: Optional[List["CreateLedgerAccountsInput"]] = Field(
        alias="childLedgerAccounts", default=None
    )
    consistency_config: Optional["LedgerAccountConsistencyConfigInput"] = Field(
        alias="consistencyConfig", default=None
    )
    currency: Optional["CurrencyMatchInput"] = None
    currency_mode: Optional[CurrencyMode] = Field(alias="currencyMode", default=None)
    ik: Any
    linked_account: Optional["ExternalAccountMatchInput"] = Field(
        alias="linkedAccount", default=None
    )
    name: str
    parent: Optional["LedgerAccountMatchInput"] = None
    type: Optional[LedgerAccountTypes] = None


class CreateLedgerInput(BaseModel):
    balance_utc_offset: Optional[Any] = Field(alias="balanceUTCOffset", default=None)
    name: str
    type: Optional[LedgerTypes] = None


class CurrencyFilter(BaseModel):
    equal_to: Optional["CurrencyMatchInput"] = Field(alias="equalTo", default=None)
    in_: Optional[List["CurrencyMatchInput"]] = Field(alias="in", default=None)


class CurrencyMatchInput(BaseModel):
    code: CurrencyCode
    custom_currency_id: Optional[Any] = Field(alias="customCurrencyId", default=None)


class CustomAccountInput(BaseModel):
    currency: Optional["CurrencyMatchInput"] = None
    currency_mode: Optional[CurrencyMode] = Field(alias="currencyMode", default=None)
    external_id: Any = Field(alias="externalId")
    name: str


class CustomTxInput(BaseModel):
    account: "ExternalAccountMatchInput"
    amount: Any
    currency: Optional["CurrencyMatchInput"] = None
    description: str
    external_id: Any = Field(alias="externalId")
    posted: Any


class DateFilter(BaseModel):
    equal_to: Optional[Any] = Field(alias="equalTo", default=None)
    in_: Optional[List[Any]] = Field(alias="in", default=None)


class DateTimeFilter(BaseModel):
    after: Optional[Any] = None
    before: Optional[Any] = None


class EntryGroupMatchInput(BaseModel):
    key: Any
    value: Any


class ExternalAccountFilter(BaseModel):
    equal_to: Optional["ExternalAccountMatchInput"] = Field(
        alias="equalTo", default=None
    )
    in_: Optional[List["ExternalAccountMatchInput"]] = Field(alias="in", default=None)


class ExternalAccountMatchInput(BaseModel):
    external_id: Optional[str] = Field(alias="externalId", default=None)
    id: Optional[str] = None
    link_id: Optional[str] = Field(alias="linkId", default=None)


class GroupBalanceAccountFilter(BaseModel):
    id: Optional["StringFilter"] = None
    path: Optional["StringMatchFilter"] = None


class Int96ConditionInput(BaseModel):
    eq: Optional[Any] = None
    gte: Optional[Any] = None
    lte: Optional[Any] = None


class Int96Filter(BaseModel):
    eq: Optional[Any] = None
    gte: Optional[Any] = None
    lte: Optional[Any] = None
    ne: Optional[Any] = None


class LedgerAccountConditionInput(BaseModel):
    own_balance: "Int96ConditionInput" = Field(alias="ownBalance")


class LedgerAccountConsistencyConfigInput(BaseModel):
    lines: Optional[LedgerLinesConsistencyMode] = None
    own_balance_updates: Optional[BalanceUpdateConsistencyMode] = Field(
        alias="ownBalanceUpdates", default=None
    )


class LedgerAccountFilter(BaseModel):
    equal_to: Optional["LedgerAccountMatchInput"] = Field(alias="equalTo", default=None)
    in_: Optional[List["LedgerAccountMatchInput"]] = Field(alias="in", default=None)


class LedgerAccountMatchInput(BaseModel):
    id: Optional[str] = None
    ledger: Optional["LedgerMatchInput"] = None
    path: Optional[str] = None


class LedgerAccountTypeFilter(BaseModel):
    equal_to: Optional[LedgerAccountTypes] = Field(alias="equalTo", default=None)
    in_: Optional[List[LedgerAccountTypes]] = Field(alias="in", default=None)


class LedgerAccountsFilterSet(BaseModel):
    has_parent_ledger_account: Optional[bool] = Field(
        alias="hasParentLedgerAccount", default=None
    )
    is_linked_account: Optional[bool] = Field(alias="isLinkedAccount", default=None)
    ledger_account: Optional["LedgerAccountFilter"] = Field(
        alias="ledgerAccount", default=None
    )
    linked_account: Optional["ExternalAccountFilter"] = Field(
        alias="linkedAccount", default=None
    )
    parent_ledger_account: Optional["LedgerAccountFilter"] = Field(
        alias="parentLedgerAccount", default=None
    )
    path: Optional["StringMatchFilter"] = None
    type: Optional["LedgerAccountTypeFilter"] = None


class LedgerEntriesFilterSet(BaseModel):
    date: Optional["DateFilter"] = None
    ledger_entry: Optional["LedgerEntryFilter"] = Field(
        alias="ledgerEntry", default=None
    )
    posted: Optional["DateTimeFilter"] = None
    tag: Optional["TagFilter"] = None
    type: Optional["StringFilter"] = None


class LedgerEntryConditionInput(BaseModel):
    account: "LedgerAccountMatchInput"
    currency: Optional["CurrencyMatchInput"] = None
    postcondition: Optional["LedgerAccountConditionInput"] = None
    precondition: Optional["LedgerAccountConditionInput"] = None


class LedgerEntryFilter(BaseModel):
    equal_to: Optional["LedgerEntryMatchInput"] = Field(alias="equalTo", default=None)
    in_: Optional[List["LedgerEntryMatchInput"]] = Field(alias="in", default=None)


class LedgerEntryGroupBalanceFilterSet(BaseModel):
    account: Optional["GroupBalanceAccountFilter"] = None
    currency: Optional["CurrencyFilter"] = None
    own_balance: Optional["Int96Filter"] = Field(alias="ownBalance", default=None)


class LedgerEntryGroupInput(BaseModel):
    key: Any
    value: Any


class LedgerEntryGroupMatchInput(BaseModel):
    key: Any
    ledger: "LedgerMatchInput"
    value: Any


class LedgerEntryGroupsFilterSet(BaseModel):
    created: Optional["DateTimeFilter"] = None
    key: Optional["StringFilter"] = None


class LedgerEntryInput(BaseModel):
    conditions: Optional[List["LedgerEntryConditionInput"]] = None
    description: Optional[str] = None
    groups: Optional[List["LedgerEntryGroupInput"]] = None
    ledger: Optional["LedgerMatchInput"] = None
    lines: Optional[List["LedgerLineInput"]] = None
    parameters: Optional[Any] = None
    posted: Optional[Any] = None
    tags: Optional[List["LedgerEntryTagInput"]] = None
    type: Optional[str] = None


class LedgerEntryMatchInput(BaseModel):
    id: Optional[str] = None
    ik: Optional[Any] = None
    ledger: Optional["LedgerMatchInput"] = None


class LedgerEntryTagInput(BaseModel):
    key: Any
    value: Any


class LedgerLineInput(BaseModel):
    account: "LedgerAccountMatchInput"
    amount: Optional[Any] = None
    currency: Optional["CurrencyMatchInput"] = None
    description: Optional[str] = None
    key: Optional[str] = None
    tx: Optional["TxMatchInput"] = None


class LedgerLineMatchInput(BaseModel):
    id: str


class LedgerLinesFilterSet(BaseModel):
    date: Optional["DateFilter"] = None
    key: Optional["StringFilter"] = None
    posted: Optional["DateTimeFilter"] = None
    type: Optional["TxTypeFilter"] = None


class LedgerMatchInput(BaseModel):
    id: Optional[str] = None
    ik: Optional[Any] = None


class LedgerTypeFilter(BaseModel):
    equal_to: Optional[LedgerTypes] = Field(alias="equalTo", default=None)
    in_: Optional[List[LedgerTypes]] = Field(alias="in", default=None)


class LedgersFilterSet(BaseModel):
    has_schema: Optional[bool] = Field(alias="hasSchema", default=None)
    type: Optional["LedgerTypeFilter"] = None


class LinkMatchInput(BaseModel):
    id: str


class SceneEntryInput(BaseModel):
    parameters: Optional[Any] = None
    type: Any


class SceneEventInput(BaseModel):
    entry: "SceneEntryInput"
    event_type: SceneEventType = Field(alias="eventType")


class SceneInput(BaseModel):
    events: List["SceneEventInput"]
    name: str


class SchemaConditionInput(BaseModel):
    own_balance: Optional["SchemaInt96ConditionInput"] = Field(
        alias="ownBalance", default=None
    )


class SchemaConsistencyConfigInput(BaseModel):
    entries: Optional[SchemaConsistencyMode] = None


class SchemaCurrencyMatchInput(BaseModel):
    code: Any
    custom_currency_id: Optional[Any] = Field(alias="customCurrencyId", default=None)


class SchemaExternalAccountMatchInput(BaseModel):
    external_id: Optional[Any] = Field(alias="externalId", default=None)
    id: Optional[Any] = None
    link_id: Optional[Any] = Field(alias="linkId", default=None)


class SchemaInput(BaseModel):
    chart_of_accounts: "ChartOfAccountsInput" = Field(alias="chartOfAccounts")
    consistency_config: Optional["SchemaConsistencyConfigInput"] = Field(
        alias="consistencyConfig", default=None
    )
    key: Any
    ledger_entries: Optional["SchemaLedgerEntriesInput"] = Field(
        alias="ledgerEntries", default=None
    )
    name: Optional[Any] = None
    scenes: Optional[List["SceneInput"]] = None


class SchemaInt96ConditionInput(BaseModel):
    eq: Optional[Any] = None
    gte: Optional[Any] = None
    lte: Optional[Any] = None


class SchemaLedgerAccountInput(BaseModel):
    children: Optional[List["SchemaLedgerAccountInput"]] = None
    consistency_config: Optional["LedgerAccountConsistencyConfigInput"] = Field(
        alias="consistencyConfig", default=None
    )
    currency: Optional["SchemaCurrencyMatchInput"] = None
    currency_mode: Optional[CurrencyMode] = Field(alias="currencyMode", default=None)
    key: Any
    linked_account: Optional["SchemaExternalAccountMatchInput"] = Field(
        alias="linkedAccount", default=None
    )
    name: Optional[Any] = None
    template: Optional[bool] = None
    type: Optional[LedgerAccountTypes] = None


class SchemaLedgerAccountMatchInput(BaseModel):
    path: Any


class SchemaLedgerEntriesInput(BaseModel):
    types: List["SchemaLedgerEntryInput"]


class SchemaLedgerEntryConditionInput(BaseModel):
    account: "SchemaLedgerAccountMatchInput"
    currency: Optional["SchemaCurrencyMatchInput"] = None
    postcondition: Optional["SchemaConditionInput"] = None
    precondition: Optional["SchemaConditionInput"] = None


class SchemaLedgerEntryGroupInput(BaseModel):
    key: Any
    value: Any


class SchemaLedgerEntryInput(BaseModel):
    conditions: Optional[List["SchemaLedgerEntryConditionInput"]] = None
    description: Optional[Any] = None
    groups: Optional[List["SchemaLedgerEntryGroupInput"]] = None
    lines: Optional[List["SchemaLedgerLineInput"]] = None
    parameters: Optional[Any] = None
    tags: Optional[List["SchemaLedgerEntryTagInput"]] = None
    type: Any


class SchemaLedgerEntryTagInput(BaseModel):
    key: Any
    value: Any


class SchemaLedgerLineInput(BaseModel):
    account: "SchemaLedgerAccountMatchInput"
    amount: Optional[Any] = None
    currency: Optional["SchemaCurrencyMatchInput"] = None
    description: Optional[Any] = None
    key: Any
    tx: Optional["SchemaTxMatchInput"] = None


class SchemaMatchInput(BaseModel):
    key: Any
    version: Optional[int] = None


class SchemaTxMatchInput(BaseModel):
    external_id: Optional[Any] = Field(alias="externalId", default=None)
    id: Optional[Any] = None


class StringFilter(BaseModel):
    equal_to: Optional[str] = Field(alias="equalTo", default=None)
    in_: Optional[List[str]] = Field(alias="in", default=None)


class StringMatchFilter(BaseModel):
    equal_to: Optional[str] = Field(alias="equalTo", default=None)
    in_: Optional[List[str]] = Field(alias="in", default=None)
    matches: Optional[str] = None


class TagFilter(BaseModel):
    equal_to: Optional["TagMatchInput"] = Field(alias="equalTo", default=None)
    in_: Optional[List["TagMatchInput"]] = Field(alias="in", default=None)


class TagMatchInput(BaseModel):
    key: Any
    value: Any


class TxMatchInput(BaseModel):
    account_id: Optional[str] = Field(alias="accountId", default=None)
    external_account_id: Optional[str] = Field(alias="externalAccountId", default=None)
    external_id: Optional[str] = Field(alias="externalId", default=None)
    id: Optional[str] = None
    link_id: Optional[str] = Field(alias="linkId", default=None)


class TxTypeFilter(BaseModel):
    equal_to: Optional[TxType] = Field(alias="equalTo", default=None)
    in_: Optional[List[TxType]] = Field(alias="in", default=None)


class UpdateLedgerAccountInput(BaseModel):
    consistency_config: Optional["LedgerAccountConsistencyConfigInput"] = Field(
        alias="consistencyConfig", default=None
    )
    name: Optional[str] = None


class UpdateLedgerEntryInput(BaseModel):
    groups: Optional[List["LedgerEntryGroupInput"]] = None
    tags: Optional[List["LedgerEntryTagInput"]] = None


class UpdateLedgerInput(BaseModel):
    name: Optional[str] = None
