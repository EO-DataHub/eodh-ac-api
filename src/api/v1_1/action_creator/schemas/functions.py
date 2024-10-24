from __future__ import annotations

from enum import StrEnum, auto
from typing import Any

from pydantic import BaseModel, Field


class FuncInputOutputType(StrEnum):
    number = auto()
    string = auto()
    boolean = auto()
    datetime = auto()
    polygon = auto()
    file = auto()
    directory = auto()


class FunctionOutputType(StrEnum):
    file = auto()
    directory = auto()


class FuncInputSpec(BaseModel):
    name: str
    description: str
    type: FuncInputOutputType
    required: bool = True
    default: Any | None = None
    options: list[Any] | None = None


class FuncOutputSpec(BaseModel):
    name: str
    type: FuncInputOutputType
    description: str | None = None


class FunctionCategory(StrEnum):
    raster_ops = "Raster Operations"
    vector_ops = "Vector Operations"
    band_math = "Band Math"
    other = "Other"


class ActionCreatorFunctionSpec(BaseModel):
    name: str
    identifier: str
    category: FunctionCategory
    tags: list[str] = Field(default_factory=list)
    standalone: bool = False
    description: str | None = None
    inputs: dict[str, FuncInputSpec]
    outputs: dict[str, FuncOutputSpec]


class FunctionsResponse(BaseModel):
    functions: list[ActionCreatorFunctionSpec]
    total: int
