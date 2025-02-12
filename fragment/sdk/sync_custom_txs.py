# Generated by fragment (with the help of ariadne-codegen)
# Source: queries/

from typing import Any, List, Literal, Union

from pydantic import Field

from .base_model import BaseModel


class SyncCustomTxs(BaseModel):
    sync_custom_txs: Union[
        "SyncCustomTxsSyncCustomTxsBadRequestError",
        "SyncCustomTxsSyncCustomTxsInternalError",
        "SyncCustomTxsSyncCustomTxsSyncCustomTxsResult",
    ] = Field(alias="syncCustomTxs", discriminator="typename__")


class SyncCustomTxsSyncCustomTxsBadRequestError(BaseModel):
    typename__: Literal["BadRequestError"] = Field(alias="__typename")


class SyncCustomTxsSyncCustomTxsInternalError(BaseModel):
    typename__: Literal["InternalError"] = Field(alias="__typename")


class SyncCustomTxsSyncCustomTxsSyncCustomTxsResult(BaseModel):
    typename__: Literal["SyncCustomTxsResult"] = Field(alias="__typename")
    txs: List["SyncCustomTxsSyncCustomTxsSyncCustomTxsResultTxs"]


class SyncCustomTxsSyncCustomTxsSyncCustomTxsResultTxs(BaseModel):
    typename__: Literal["Tx"] = Field(alias="__typename")
    link_id: str = Field(alias="linkId")
    id: str
    external_id: str = Field(alias="externalId")
    external_account_id: str = Field(alias="externalAccountId")
    amount: Any
    description: str
    posted: Any


SyncCustomTxs.model_rebuild()
SyncCustomTxsSyncCustomTxsSyncCustomTxsResult.model_rebuild()
