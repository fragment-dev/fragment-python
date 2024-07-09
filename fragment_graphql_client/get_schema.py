# Generated by ariadne-codegen
# Source: queries/

from typing import Any, Optional

from pydantic import Field

from .base_model import BaseModel


class GetSchema(BaseModel):
    schema_: Optional["GetSchemaSchema"] = Field(alias="schema")


class GetSchemaSchema(BaseModel):
    key: Any
    name: str
    version: "GetSchemaSchemaVersion"


class GetSchemaSchemaVersion(BaseModel):
    created: Any
    version: int
    json_: Any = Field(alias="json")


GetSchema.model_rebuild()
GetSchemaSchema.model_rebuild()
