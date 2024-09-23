from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class FuncParameterSpec(BaseModel):
    type: str
    required: bool = True
    description: str
    default: Any | None = None
    options: list[Any] | None = None


class ActionCreatorFunctionSpec(BaseModel):
    name: str
    parameters: dict[str, FuncParameterSpec]


class FunctionsResponse(BaseModel):
    functions: list[ActionCreatorFunctionSpec]
    total: int
