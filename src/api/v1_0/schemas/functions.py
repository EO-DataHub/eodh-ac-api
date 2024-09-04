from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi_hypermodel import FrozenDict, HALFor, HALHyperModel, HALLinks
from pydantic import BaseModel


class RasterCalculatorIndex(str, Enum):
    evi = "EVI"
    ndvi = "NDVI"
    ndwi = "NDWI"
    savi = "SAVI"


class FuncParameterSpec(BaseModel):
    type: str
    required: bool = True
    description: str
    default: Any | None = None
    options: list[Any] | None = None


class ActionCreatorFunctionSpec(BaseModel):
    name: str
    supported_collections: list[str]
    parameters: dict[str, FuncParameterSpec]


class FunctionCollection(HALHyperModel):
    functions: list[ActionCreatorFunctionSpec]

    links: HALLinks = FrozenDict({
        "self": HALFor("get_available_functions"),
    })
