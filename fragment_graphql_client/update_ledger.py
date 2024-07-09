# Generated by ariadne-codegen
# Source: queries/

from typing import Any, Literal, Union

from pydantic import Field

from .base_model import BaseModel


class UpdateLedger(BaseModel):
    update_ledger: Union[
        "UpdateLedgerUpdateLedgerBadRequestError",
        "UpdateLedgerUpdateLedgerInternalError",
        "UpdateLedgerUpdateLedgerUpdateLedgerResult",
    ] = Field(alias="updateLedger", discriminator="typename__")


class UpdateLedgerUpdateLedgerBadRequestError(BaseModel):
    typename__: Literal["BadRequestError"] = Field(alias="__typename")


class UpdateLedgerUpdateLedgerInternalError(BaseModel):
    typename__: Literal["InternalError"] = Field(alias="__typename")


class UpdateLedgerUpdateLedgerUpdateLedgerResult(BaseModel):
    typename__: Literal["UpdateLedgerResult"] = Field(alias="__typename")
    ledger: "UpdateLedgerUpdateLedgerUpdateLedgerResultLedger"


class UpdateLedgerUpdateLedgerUpdateLedgerResultLedger(BaseModel):
    id: str
    ik: Any
    name: str


UpdateLedger.model_rebuild()
UpdateLedgerUpdateLedgerUpdateLedgerResult.model_rebuild()
