# Generated by fragment (with the help of ariadne-codegen)
# Source: queries/

from typing import Any, Optional

from pydantic import Field

from .base_model import BaseModel


class GetLedger(BaseModel):
    ledger: Optional["GetLedgerLedger"]


class GetLedgerLedger(BaseModel):
    id: str
    ik: Any
    name: str
    created: Any
    balance_utc_offset: Any = Field(alias="balanceUTCOffset")


GetLedger.model_rebuild()
