from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from enum import Enum
from typing import Any

from geojson_pydantic.geometries import Geometry, Polygon
from pydantic import BaseModel, model_validator

from src.services.validation_utils import (
    aoi_from_bbox_if_necessary,
    aoi_from_geojson_if_necessary,
    ensure_area_smaller_than,
    raise_if_both_aoi_and_bbox_provided,
    validate_aoi_or_bbox_provided,
    validate_stac_collection,
)


class FuncInputOutputType(str, Enum):
    number = "number"
    string = "string"
    boolean = "boolean"
    datetime = "datetime"
    stac_collection = "stac_collection"


class FuncInputSpec(BaseModel):
    type: FuncInputOutputType
    required: bool = True
    description: str
    default: Any | None = None
    options: list[Any] | None = None


class FuncOutputSpec(BaseModel):
    type: FuncInputOutputType
    description: str | None = None


class ActionCreatorFunctionSpec(BaseModel):
    name: str
    identifier: str
    preset: bool = False
    description: str | None = None
    inputs: dict[str, FuncInputSpec]
    outputs: dict[str, FuncOutputSpec]


class FunctionsResponse(BaseModel):
    functions: list[ActionCreatorFunctionSpec]
    total: int


class RasterCalculatorIndex(str, Enum):
    NDVI = "NDVI"
    EVI = "EVI"
    NDWI = "NDWI"
    SAVI = "SAVI"


class RasterCalculatorFunctionInputs(BaseModel):
    aoi: Geometry
    bbox: tuple[float, float, float, float] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    collection: str
    index: RasterCalculatorIndex = RasterCalculatorIndex.NDVI

    @model_validator(mode="before")
    @classmethod
    def validate_aoi(cls, v: dict[str, Any]) -> dict[str, Any]:
        # Neither AOI nor BBox provided
        validate_aoi_or_bbox_provided(v)

        # Both AOI and BBox provided
        raise_if_both_aoi_and_bbox_provided(v)

        # AOI from bbox
        v = aoi_from_bbox_if_necessary(v)

        # AOI from GeoJSON
        v = aoi_from_geojson_if_necessary(v)

        # Ensure AOI or BBox (for non polygon features) does not exceed area limit
        geom_to_check = v["aoi"] if v["aoi"].type in {"Polygon", "MultiPolygon"} else Polygon.from_bounds(*v["bbox"])
        ensure_area_smaller_than(geom_to_check.model_dump())

        # Validate STAC collection
        validate_stac_collection(
            specified_collection=v["collection"],
            function_name="raster-calculate",
        )

        return v

    def as_inputs(self) -> dict[str, Any]:
        return {
            "aoi": self.aoi.model_dump_json(),
            "stac_collection": self.collection,
            "date_start": self.date_from,
            "date_end": self.date_to,
            "index": self.index,
        }


FUNCTION_TO_INPUTS_LOOKUP = {
    "raster-calculate": RasterCalculatorFunctionInputs,
}
