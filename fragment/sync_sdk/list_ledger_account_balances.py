# Generated by fragment (with the help of ariadne-codegen)
# Source: queries/

from typing import Any, List, Optional

from pydantic import Field

from .base_model import BaseModel
from .enums import LedgerAccountTypes


class ListLedgerAccountBalances(BaseModel):
    ledger: Optional["ListLedgerAccountBalancesLedger"]


class ListLedgerAccountBalancesLedger(BaseModel):
    id: str
    ik: Any
    name: str
    created: Any
    ledger_accounts: "ListLedgerAccountBalancesLedgerLedgerAccounts" = Field(
        alias="ledgerAccounts"
    )


class ListLedgerAccountBalancesLedgerLedgerAccounts(BaseModel):
    nodes: List["ListLedgerAccountBalancesLedgerLedgerAccountsNodes"]
    page_info: "ListLedgerAccountBalancesLedgerLedgerAccountsPageInfo" = Field(
        alias="pageInfo"
    )


class ListLedgerAccountBalancesLedgerLedgerAccountsNodes(BaseModel):
    id: str
    path: str
    name: Optional[str]
    type: LedgerAccountTypes
    created: Any
    own_balance: Any = Field(alias="ownBalance")
    child_balance: Any = Field(alias="childBalance")
    balance: Any


class ListLedgerAccountBalancesLedgerLedgerAccountsPageInfo(BaseModel):
    has_next_page: bool = Field(alias="hasNextPage")
    end_cursor: Optional[str] = Field(alias="endCursor")
    has_previous_page: bool = Field(alias="hasPreviousPage")
    start_cursor: Optional[str] = Field(alias="startCursor")


ListLedgerAccountBalances.model_rebuild()
ListLedgerAccountBalancesLedger.model_rebuild()
ListLedgerAccountBalancesLedgerLedgerAccounts.model_rebuild()
