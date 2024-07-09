# Generated by ariadne-codegen
# Source: queries/

from typing import Any, List, Literal, Optional, Union

from pydantic import Field

from .base_model import BaseModel


class AddLedgerEntry(BaseModel):
    add_ledger_entry: Union[
        "AddLedgerEntryAddLedgerEntryAddLedgerEntryResult",
        "AddLedgerEntryAddLedgerEntryBadRequestError",
        "AddLedgerEntryAddLedgerEntryInternalError",
    ] = Field(alias="addLedgerEntry", discriminator="typename__")


class AddLedgerEntryAddLedgerEntryAddLedgerEntryResult(BaseModel):
    typename__: Literal["AddLedgerEntryResult"] = Field(alias="__typename")
    is_ik_replay: bool = Field(alias="isIkReplay")
    entry: "AddLedgerEntryAddLedgerEntryAddLedgerEntryResultEntry"
    lines: List["AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLines"]


class AddLedgerEntryAddLedgerEntryAddLedgerEntryResultEntry(BaseModel):
    type: Optional[Any]
    id: str
    ik: str
    posted: Any
    created: Any


class AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLines(BaseModel):
    id: str
    amount: Any
    account: "AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLinesAccount"


class AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLinesAccount(BaseModel):
    path: str


class AddLedgerEntryAddLedgerEntryBadRequestError(BaseModel):
    typename__: Literal["BadRequestError"] = Field(alias="__typename")


class AddLedgerEntryAddLedgerEntryInternalError(BaseModel):
    typename__: Literal["InternalError"] = Field(alias="__typename")


AddLedgerEntry.model_rebuild()
AddLedgerEntryAddLedgerEntryAddLedgerEntryResult.model_rebuild()
AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLines.model_rebuild()
