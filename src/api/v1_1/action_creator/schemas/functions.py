from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto
from typing import Annotated, Any

from pydantic import BaseModel, Field


class FuncInputOutputType(StrEnum):
    number = auto()
    string = auto()
    boolean = auto()
    datetime = auto()
    polygon = auto()
    file = auto()
    directory = auto()


class ConstraintOperator(StrEnum):
    gt = auto()
    ge = auto()
    lt = auto()
    le = auto()
    min_length = auto()
    max_length = auto()


class FunctionInputConstraint(BaseModel):
    operator: ConstraintOperator
    value: int | float | str | datetime


class FunctionOutputType(StrEnum):
    file = auto()
    directory = auto()


class FunctionInputOption(BaseModel):
    label: str
    value: Any


class FunctionInputSpec(BaseModel):
    name: str
    description: str
    type: FuncInputOutputType
    required: bool = True
    default: Any | None = None
    options: list[FunctionInputOption] | None = None
    constraints: list[FunctionInputConstraint] = Field(default_factory=list)


class FuncOutputSpec(BaseModel):
    name: str
    type: FuncInputOutputType
    description: str | None = None


class FunctionCategory(StrEnum):
    data_select = "Data Selection"
    raster_ops = "Raster Operations"
    vector_ops = "Vector Operations"
    spectral_indices = "Spectral Indices"
    other = "Other"


class ActionCreatorFunctionSpec(BaseModel):
    name: str
    identifier: str
    category: FunctionCategory
    tags: list[str] = Field(default_factory=list)
    description: str | None = None
    inputs: dict[str, FunctionInputSpec]
    outputs: dict[str, FuncOutputSpec]
    visible: Annotated[bool, Field(default=False, validate_default=True)]


class FunctionsResponse(BaseModel):
    functions: list[ActionCreatorFunctionSpec]
    total: int
