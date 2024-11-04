from __future__ import annotations

import abc
from datetime import datetime  # noqa: TCH003
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Annotated, Any, Generic, Literal, Sequence, TypeVar, Union

from geojson_pydantic.geometries import Polygon
from pydantic import BaseModel, Field, field_validator, model_validator

from src.consts.functions import FUNCTIONS_REGISTRY
from src.services.validation_utils import (
    aoi_must_be_present,
    ensure_area_smaller_than,
    validate_date_range,
    validate_stac_collection_v1_1,
)

if TYPE_CHECKING:
    from pydantic_core.core_schema import ValidationInfo

T = TypeVar("T", bound=BaseModel)

DEFAULT_PAGE_IDX = 1
MIN_PAGE_IDX = 1
DEFAULT_RESULTS_PER_PAGE = 25
MIN_RESULTS_PER_PAGE = 1
MAX_RESULTS_PER_PAGE = 100


class ErrorResponse(BaseModel):
    detail: str


class FuncInputOutputType(StrEnum):
    number = auto()
    string = auto()
    boolean = auto()
    datetime = auto()
    point = auto()
    linestring = auto()
    polygon = auto()
    stac_item = auto()
    stac_collection = auto()
    stac_catalog = auto()


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
    identifier: str
    name: str
    description: str | None = None
    visible: bool = False
    standalone: bool = False
    inputs: dict[str, FuncInputSpec]
    outputs: dict[str, FuncOutputSpec]


class ActionCreatorPresetSpec(BaseModel):
    identifier: str
    name: str
    description: str | None = None
    thumbnail_b64: str | None = None
    workflow: dict[str, TWorkflowStep]


class PresetsResponse(BaseModel):
    presets: list[ActionCreatorPresetSpec]
    total: int


class FunctionsResponse(BaseModel):
    functions: list[ActionCreatorFunctionSpec]
    total: int


class OGCProcessInputs(BaseModel, abc.ABC):
    @abc.abstractmethod
    def as_ogc_process_inputs(self) -> dict[str, Any]: ...


class CommonFunctionInputs(OGCProcessInputs, abc.ABC):
    identifier: str
    aoi: Annotated[Polygon | None, Field(None, validate_default=True)]
    date_start: datetime | None = None
    date_end: datetime | None = None
    stac_collection: Annotated[str | None, Field(None, validate_default=True)]

    @field_validator("stac_collection", mode="after")
    @classmethod
    def validate_stac_collection(cls, v: str | None, info: ValidationInfo) -> str:
        if v is None:
            return FUNCTIONS_REGISTRY[info.data["identifier"]]["inputs"]["stac_collection"]["default"]  # type: ignore[no-any-return]
        # Validate STAC collection
        validate_stac_collection_v1_1(
            specified_collection=v,
            function_identifier=info.data["identifier"],
        )
        return v

    @field_validator("aoi", mode="before")
    @classmethod
    def validate_aoi(cls, v: dict[str, Any] | None = None) -> dict[str, Any]:
        # Ensure AOI provided
        aoi_must_be_present(v)

        # Ensure AOI does not exceed area limit
        geom_to_check = Polygon(**v)
        ensure_area_smaller_than(geom_to_check.model_dump())

        return v  # type: ignore[return-value]

    @field_validator("date_end", mode="after")
    @classmethod
    def validate_date_range(cls, date_end: datetime | None, info: ValidationInfo) -> datetime | None:
        date_start = info.data.get("date_start")
        validate_date_range(date_start=date_start, date_end=date_end)
        return date_end

    def as_ogc_process_inputs(self) -> dict[str, Any]:
        vals = {
            "aoi": self.aoi.model_dump_json(),  # type: ignore[union-attr]
            "stac_collection": self.stac_collection,
            "date_start": self.date_start.isoformat() if self.date_start else None,
            "date_end": self.date_end.isoformat() if self.date_end else None,
        }
        keys_to_pop = [k for k in vals if vals[k] is None]
        for k in keys_to_pop:
            vals.pop(k, None)

        return vals


class RasterCalculatorFunctionInputs(CommonFunctionInputs):
    limit: Annotated[int, Field(10, validate_default=True, ge=1, le=100)]

    def as_ogc_process_inputs(self) -> dict[str, Any]:
        outputs = super().as_ogc_process_inputs()
        outputs["limit"] = self.limit
        outputs["index"] = self.identifier
        return outputs


class LandCoverChangeDetectionFunctionInputs(CommonFunctionInputs):
    identifier: Literal["land-cover-change-detection"] = "land-cover-change-detection"

    def as_ogc_process_inputs(self) -> dict[str, Any]:
        outputs = super().as_ogc_process_inputs()
        # Rename stac_collection input to source
        stac_collection = outputs.pop("stac_collection")
        outputs["source"] = stac_collection
        return outputs


class ClipFunctionInputs(BaseModel):
    collection: str
    aoi: Annotated[Polygon | None, Field(None, validate_default=True)]

    @field_validator("aoi", mode="before")
    @classmethod
    def validate_aoi(cls, v: dict[str, Any] | None = None) -> dict[str, Any]:
        # Ensure AOI provided
        aoi_must_be_present(v)

        # Ensure AOI does not exceed area limit
        geom_to_check = Polygon(**v)
        ensure_area_smaller_than(geom_to_check.model_dump())

        return v  # type: ignore[return-value]


class ActionCreatorJobStatus(StrEnum):
    submitted = "submitted"
    running = "running"
    cancel_request = "cancel-request"
    successful = "successful"
    failed = "failed"
    cancelled = "cancelled"


class ClipWorkflowStep(BaseModel):
    identifier: Literal["clip"] = "clip"
    inputs: ClipFunctionInputs


class NDVIFunctionInputs(RasterCalculatorFunctionInputs):
    identifier: Literal["ndvi"] = "ndvi"


class NDVIWorkflowStep(BaseModel):
    identifier: Literal["ndvi"] = "ndvi"
    inputs: NDVIFunctionInputs


class EVIFunctionInputs(RasterCalculatorFunctionInputs):
    identifier: Literal["evi"] = "evi"


class EVIWorkflowStep(BaseModel):
    identifier: Literal["evi"] = "evi"
    inputs: RasterCalculatorFunctionInputs


class SAVIFunctionInputs(RasterCalculatorFunctionInputs):
    identifier: Literal["savi"] = "savi"


class SAVIWorkflowStep(BaseModel):
    identifier: Literal["savi"] = "savi"
    inputs: RasterCalculatorFunctionInputs


class NDWIFunctionInputs(RasterCalculatorFunctionInputs):
    identifier: Literal["ndwi"] = "ndwi"


class NDWIWorkflowStep(BaseModel):
    identifier: Literal["ndwi"] = "ndwi"
    inputs: RasterCalculatorFunctionInputs


class LandCoverChangeDetectionWorkflowStep(BaseModel):
    identifier: Literal["land-cover-change-detection"] = "land-cover-change-detection"
    inputs: LandCoverChangeDetectionFunctionInputs


TWorkflowStep = Annotated[
    Union[
        NDVIWorkflowStep,
        NDWIWorkflowStep,
        SAVIWorkflowStep,
        EVIWorkflowStep,
        ClipWorkflowStep,
        LandCoverChangeDetectionWorkflowStep,
    ],
    Field(discriminator="identifier"),
]


class ActionCreatorSubmissionRequest(BaseModel):
    workflow: dict[str, TWorkflowStep]


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


class OrderDirection(StrEnum):
    asc = auto()
    desc = auto()


class ActionCreatorSubmissionsQueryParams(BaseModel):
    order_by: Annotated[
        Literal["submission_id", "status", "function_identifier", "submitted_at", "finished_at", "successful"],
        Field("submitted_at", description="Field to use for ordering - `submitted_at` by default"),
    ]
    order_direction: Annotated[
        OrderDirection,
        Field("asc", description="Order direction - `asc` by default"),
    ]
    page: Annotated[
        int,
        Field(DEFAULT_PAGE_IDX, description="Page number - 1 by default", ge=MIN_PAGE_IDX),
    ]
    per_page: Annotated[
        int,
        Field(
            DEFAULT_RESULTS_PER_PAGE,
            description="Number of results to return - 25 by default",
            ge=MIN_RESULTS_PER_PAGE,
            le=MAX_RESULTS_PER_PAGE,
        ),
    ]

    @classmethod
    @field_validator("order_by", mode="before")
    def validate_order_by(cls, v: str | None) -> str:
        return "submitted_at" if v is None else v

    @classmethod
    @field_validator("order_direction", mode="before")
    def validate_order_direction(cls, v: str | None) -> str:
        return "asc" if v is None else v

    @classmethod
    @field_validator("page", mode="before")
    def validate_page(cls, v: int | None) -> int:
        return DEFAULT_PAGE_IDX if v is None else v

    @classmethod
    @field_validator("per_page", mode="before")
    def validate_per_page(cls, v: int | None) -> int:
        return DEFAULT_RESULTS_PER_PAGE if v is None else v


class PaginationResults(BaseModel, Generic[T]):
    results: Sequence[T]
    total_items: int
    current_page: int
    total_pages: int
    results_on_current_page: int
    results_per_page: int
    ordered_by: str
    order_direction: OrderDirection
