from __future__ import annotations

from typing import Any

from fastapi_hypermodel import FrozenDict, HALFor, HALHyperModel, HALLinks
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


class FunctionsResponse(HALHyperModel):
    functions: list[ActionCreatorFunctionSpec]

    links: HALLinks = FrozenDict({
        "self": HALFor("get_available_functions"),
    })
