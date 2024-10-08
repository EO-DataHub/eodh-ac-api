from __future__ import annotations

import abc
from datetime import datetime  # noqa: TCH003
from enum import Enum, StrEnum
from typing import Any, ClassVar, Sequence

from geojson_pydantic.geometries import Geometry, Polygon
from pydantic import BaseModel, Field, model_validator

from src.services.validation_utils import (
    aoi_from_bbox_if_necessary,
    aoi_from_geojson_if_necessary,
    ensure_area_smaller_than,
    raise_if_both_aoi_and_bbox_provided,
    validate_aoi_or_bbox_provided,
    validate_date_range,
    validate_stac_collection,
)


class ErrorResponse(BaseModel):
    detail: str


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
    thumbnail_b64: str | None = None
    inputs: dict[str, FuncInputSpec]
    outputs: dict[str, FuncOutputSpec]


class FunctionsResponse(BaseModel):
    functions: list[ActionCreatorFunctionSpec]
    total: int


class RasterCalculatorIndex(StrEnum):
    NDVI = "NDVI"
    EVI = "EVI"
    NDWI = "NDWI"
    SAVI = "SAVI"


class WaterQualityIndex(StrEnum):
    NDWI = "NDWI"
    CDOM = "CDOM"
    DOC = "DOC"
    CYA = "CYA"


class PresetFunctionIdentifier(StrEnum):
    RASTER_CALCULATOR = "raster-calculate"
    LAND_COVER_CHANGE_DETECTION = "lulc-change"
    WATER_QUALITY = "water-quality"


class OGCProcessInputs(BaseModel, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def validate_model(cls, v: dict[str, Any]) -> dict[str, Any]: ...

    @abc.abstractmethod
    def as_ogc_process_inputs(self) -> dict[str, Any]: ...


class CommonPresetFunctionInputs(OGCProcessInputs, abc.ABC):
    function_identifier: ClassVar[str] = "common"

    aoi: Geometry
    bbox: tuple[float, float, float, float] | None = None
    date_start: datetime | None = None
    date_end: datetime | None = None
    stac_collection: str

    @classmethod
    def validate_model(cls, v: dict[str, Any]) -> dict[str, Any]:
        # Neither AOI nor BBox provided
        validate_aoi_or_bbox_provided(v)

        # Both AOI and BBox provided
        raise_if_both_aoi_and_bbox_provided(v)

        # AOI from bbox
        v = aoi_from_bbox_if_necessary(v)

        # AOI from GeoJSON
        v = aoi_from_geojson_if_necessary(v)

        # Ensure AOI or BBox (for non polygon features) does not exceed area limit
        geom_to_check = (
            Polygon(**v["aoi"]) if v["aoi"]["type"] in {"Polygon", "MultiPolygon"} else Polygon.from_bounds(*v["bbox"])
        )
        ensure_area_smaller_than(geom_to_check.model_dump())

        # Validate STAC collection
        validate_stac_collection(
            specified_collection=v["stac_collection"],
            function_identifier=cls.function_identifier,
        )

        # Validate proper date range
        validate_date_range(v)

        return v

    @model_validator(mode="before")
    @classmethod
    def validate_before_init(cls, v: dict[str, Any]) -> dict[str, Any]:
        return cls.validate_model(v)

    def as_ogc_process_inputs(self) -> dict[str, Any]:
        vals = {
            "aoi": self.aoi.model_dump_json(),
            "stac_collection": self.stac_collection,
            "date_start": self.date_start.isoformat() if self.date_start else None,
            "date_end": self.date_end.isoformat() if self.date_end else None,
        }
        keys_to_pop = [k for k in vals if vals[k] is None]
        for k in keys_to_pop:
            vals.pop(k, None)
        return vals


class RasterCalculatorFunctionInputs(CommonPresetFunctionInputs):
    function_identifier: ClassVar[str] = PresetFunctionIdentifier.RASTER_CALCULATOR
    index: RasterCalculatorIndex = RasterCalculatorIndex.NDVI

    def as_ogc_process_inputs(self) -> dict[str, Any]:
        outputs = super().as_ogc_process_inputs()
        outputs["index"] = self.index.value
        return outputs


class LandCoverChangeDetectionFunctionInputs(CommonPresetFunctionInputs):
    function_identifier: ClassVar[str] = PresetFunctionIdentifier.LAND_COVER_CHANGE_DETECTION


class WaterQualityFunctionInputs(CommonPresetFunctionInputs):
    function_identifier: ClassVar[str] = PresetFunctionIdentifier.WATER_QUALITY
    index: WaterQualityIndex = WaterQualityIndex.NDWI
    calibrate: bool = False

    def as_ogc_process_inputs(self) -> dict[str, Any]:
        outputs = super().as_ogc_process_inputs()
        outputs["index"] = self.index.value
        outputs["calibrate"] = self.calibrate
        return outputs


FUNCTION_TO_INPUTS_LOOKUP = {
    PresetFunctionIdentifier.RASTER_CALCULATOR: RasterCalculatorFunctionInputs,
    PresetFunctionIdentifier.LAND_COVER_CHANGE_DETECTION: LandCoverChangeDetectionFunctionInputs,
    PresetFunctionIdentifier.WATER_QUALITY: WaterQualityFunctionInputs,
}


class ActionCreatorJobStatus(str, Enum):
    submitted = "submitted"
    running = "running"
    cancel_request = "cancel-request"
    successful = "successful"
    failed = "failed"
    cancelled = "cancelled"


class PresetFunctionExecutionRequest(BaseModel):
    function_identifier: PresetFunctionIdentifier
    inputs: dict[str, Any] = Field(
        ...,
        examples=[
            {
                "stac_collection": "sentinel-2-l2a",
                "aoi": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [14.763294437090849, 50.833598186651244],
                            [15.052268923898112, 50.833598186651244],
                            [15.052268923898112, 50.989077215056824],
                            [14.763294437090849, 50.989077215056824],
                            [14.763294437090849, 50.833598186651244],
                        ]
                    ],
                },
                "date_start": "2024-04-03T00:00:00",
                "date_end": "2024-08-01T00:00:00",
                "index": "NDVI",
            }
        ],
    )

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, v: dict[str, Any]) -> dict[str, Any]:
        if v["function_identifier"] not in FUNCTION_TO_INPUTS_LOOKUP:
            msg = (
                f"Function {v['function_identifier']} not recognized. "
                "Please use `get_available_functions` endpoint to get list of valid functions"
            )
            raise ValueError(msg)

        inputs = v["inputs"]
        inputs_cls = FUNCTION_TO_INPUTS_LOOKUP[v["function_identifier"]]
        inputs = inputs_cls.validate_model(inputs)
        v["inputs"] = inputs
        return v


class ActionCreatorSubmissionRequest(BaseModel):
    preset_function: PresetFunctionExecutionRequest


class ActionCreatorJob(BaseModel):
    submission_id: str
    spec: ActionCreatorSubmissionRequest
    status: ActionCreatorJobStatus = ActionCreatorJobStatus.submitted
    submitted_at: datetime
    running_at: datetime | None = None
    finished_at: datetime | None = None
    successful: bool | None = None


class ActionCreatorJobSummary(BaseModel):
    submission_id: str
    status: ActionCreatorJobStatus
    function_identifier: str
    submitted_at: datetime
    finished_at: datetime | None = None
    successful: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def resolve_job_success_flag(cls, v: dict[str, Any]) -> dict[str, Any]:
        status = v.get("status")
        if status is None:
            v["successful"] = None
        elif status == "failed":
            v["successful"] = False
        elif status == "successful":
            v["successful"] = True
        else:
            v["successful"] = None
        return v


class ActionCreatorJobsResponse(BaseModel):
    submitted_jobs: Sequence[ActionCreatorJobSummary]
    total: int
