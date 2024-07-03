# Generated by ariadne-codegen
# Source: queries/queries.graphql

from typing import Any, Literal, Union

from pydantic import Field

from .base_model import BaseModel


class StoreSchema(BaseModel):
    store_schema: Union[
        "StoreSchemaStoreSchemaBadRequestError",
        "StoreSchemaStoreSchemaInternalError",
        "StoreSchemaStoreSchemaStoreSchemaResult",
    ] = Field(alias="storeSchema", discriminator="typename__")


class StoreSchemaStoreSchemaBadRequestError(BaseModel):
    typename__: Literal["BadRequestError"] = Field(alias="__typename")


class StoreSchemaStoreSchemaInternalError(BaseModel):
    typename__: Literal["InternalError"] = Field(alias="__typename")


class StoreSchemaStoreSchemaStoreSchemaResult(BaseModel):
    typename__: Literal["StoreSchemaResult"] = Field(alias="__typename")
    schema_: "StoreSchemaStoreSchemaStoreSchemaResultSchema" = Field(alias="schema")


class StoreSchemaStoreSchemaStoreSchemaResultSchema(BaseModel):
    key: Any
    name: str
    version: "StoreSchemaStoreSchemaStoreSchemaResultSchemaVersion"


class StoreSchemaStoreSchemaStoreSchemaResultSchemaVersion(BaseModel):
    created: Any
    version: int


StoreSchema.model_rebuild()
StoreSchemaStoreSchemaStoreSchemaResult.model_rebuild()
StoreSchemaStoreSchemaStoreSchemaResultSchema.model_rebuild()
