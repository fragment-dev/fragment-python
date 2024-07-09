# Generated by ariadne-codegen
# Source: queries/

from typing import Any, List, Literal, Optional, Union

from pydantic import Field

from .base_model import BaseModel


class ReconcileTx(BaseModel):
    reconcile_tx: Union[
        "ReconcileTxReconcileTxBadRequestError",
        "ReconcileTxReconcileTxInternalError",
        "ReconcileTxReconcileTxReconcileTxResult",
    ] = Field(alias="reconcileTx", discriminator="typename__")


class ReconcileTxReconcileTxBadRequestError(BaseModel):
    typename__: Literal["BadRequestError"] = Field(alias="__typename")


class ReconcileTxReconcileTxInternalError(BaseModel):
    typename__: Literal["InternalError"] = Field(alias="__typename")


class ReconcileTxReconcileTxReconcileTxResult(BaseModel):
    typename__: Literal["ReconcileTxResult"] = Field(alias="__typename")
    entry: "ReconcileTxReconcileTxReconcileTxResultEntry"
    lines: List["ReconcileTxReconcileTxReconcileTxResultLines"]


class ReconcileTxReconcileTxReconcileTxResultEntry(BaseModel):
    id: str
    ik: str
    date: Any
    posted: Any
    created: Any
    description: Optional[str]


class ReconcileTxReconcileTxReconcileTxResultLines(BaseModel):
    id: str
    amount: Any
    account: "ReconcileTxReconcileTxReconcileTxResultLinesAccount"
    external_tx_id: Optional[str] = Field(alias="externalTxId")


class ReconcileTxReconcileTxReconcileTxResultLinesAccount(BaseModel):
    path: str


ReconcileTx.model_rebuild()
ReconcileTxReconcileTxReconcileTxResult.model_rebuild()
ReconcileTxReconcileTxReconcileTxResultLines.model_rebuild()
