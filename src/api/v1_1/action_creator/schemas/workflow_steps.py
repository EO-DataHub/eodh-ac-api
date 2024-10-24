from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from enum import StrEnum, auto
from typing import Annotated, Any, Literal, Union

from geojson_pydantic import Polygon  # noqa: TCH002
from pydantic import BaseModel, Field
from pyproj.database import query_crs_info

from src.api.v1_1.action_creator.schemas.functions import FunctionOutputType  # noqa: TCH001


def get_crs_list() -> list[str]:
    crs_info_list = query_crs_info(auth_name=None, pj_types=None)
    crs_list = [f"EPSG:{info[1]}" for info in crs_info_list]
    return sorted(crs_list)


EPSG_CODES = get_crs_list()


class WorkflowStepBase(BaseModel):
    identifier: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]


class WorkflowStepsResponse(BaseModel):
    steps: list[Any]
    total: int


class ValueType(StrEnum):
    ref = auto()
    atom = auto()


class InputValue(BaseModel):
    type: ValueType = Field(ValueType.atom, alias="$type")
    value: Any | None = None


class StepInputSpec(BaseModel):
    name: str
    value: InputValue


class StepOutputSpec(BaseModel):
    name: str
    type: FunctionOutputType


class WorkflowStep(BaseModel):
    identifier: str
    inputs: dict[str, StepInputSpec]
    outputs: dict[str, StepOutputSpec]


class OrbitDirection(StrEnum):
    ascending = auto()
    descending = auto()


class Polarization(StrEnum):
    vv = "VV"
    vv_vh = "VV+VH"
    hh = "HH"
    hh_hv = "HH+HV"


class Sentinel1QueryStepInputs(BaseModel):
    stac_collection: Literal["sentinel-1-grd"] = "sentinel-1-grd"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="2014-10-10")]
    date_end: datetime | None
    orbit_direction: list[OrbitDirection]
    polarization: list[Polarization]
    limit: int | None = 10


class DirectoryStepOutputSpec(BaseModel):
    type: Literal["directory"] = "directory"
    name: Literal["results"] = "results"


class DirectoryOutputs(BaseModel):
    results: DirectoryStepOutputSpec


class Sentinel2QueryStepInputs(BaseModel):
    stac_collection: Literal["sentinel-2-l1c", "sentinel-2-l2a"] = "sentinel-2-l2a"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="2015-06-27")]
    date_end: datetime | None
    cloud_cover_min: Annotated[int, Field(default=0, ge=0, le=100)]
    cloud_cover_max: Annotated[int, Field(default=0, ge=0, le=100)]
    limit: int | None = 10


class GlobalLandCoverQueryStepInputs(BaseModel):
    stac_collection: Literal["esa-lccci-glcm"] = "esa-lccci-glcm"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="1992-01-01T00:00:00", le="2015-12-31T23:59:59")]
    date_end: Annotated[datetime | None, Field(None, ge="1992-01-01T00:00:00", le="2015-12-31T23:59:59")]
    limit: int | None = 10


class CorineLandCoverQueryStepInputs(BaseModel):
    stac_collection: Literal["clms-corine-lc"] = "clms-corine-lc"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="1990-01-01T00:00:00", le="2018-12-31T23:59:59")]
    date_end: Annotated[datetime | None, Field(None, ge="1990-01-01T00:00:00", le="2018-12-31T23:59:59")]
    limit: int | None = 10


class WaterBodiesQueryStep(BaseModel):
    stac_collection: Literal["clms-water-bodies"] = "clms-water-bodies"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="2020-01-01T00:00:00")]
    date_end: Annotated[datetime | None, Field(None, ge="2020-01-01T00:00:00")]
    limit: int | None = 10


TQueryStep = Union[
    Sentinel1QueryStepInputs,
    Sentinel2QueryStepInputs,
    GlobalLandCoverQueryStepInputs,
    CorineLandCoverQueryStepInputs,
    WaterBodiesQueryStep,
]


class DatasetQueryStep(BaseModel):
    identifier: Literal[
        "s1-ds-query",
        "s2-ds-query",
        "esa-glc-ds-query",
        "corine-lc-ds-query",
        "water-bodies-ds-query",
    ]
    inputs: TQueryStep
    outputs: DirectoryOutputs


class DataDirInput(BaseModel):
    name: Literal["data_dir"] = "data_dir"
    type: Literal["directory"] = "directory"


class DirectoryInputs(BaseModel):
    data_dir: DataDirInput


class NDVIStep(BaseModel):
    identifier: Literal["ndvi"] = "ndvi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs


class EVIStep(BaseModel):
    identifier: Literal["evi"] = "evi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs


class NDWIStep(BaseModel):
    identifier: Literal["ndwi"] = "ndwi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs


class SAVIStep(BaseModel):
    identifier: Literal["savi"] = "savi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs


class ClipInputs(BaseModel):
    data_dir: DataDirInput
    aoi: Polygon


class ClipStep(BaseModel):
    identifier: Literal["clip"] = "clip"
    inputs: ClipInputs
    outputs: DirectoryOutputs


class ReprojectInputs(BaseModel):
    data_dir: DataDirInput
    epsg: Literal[*EPSG_CODES] = "EPSG:4326"  # type: ignore[valid-type]


class ReprojectStep(BaseModel):
    identifier: Literal["reproject"] = "reproject"
    inputs: ReprojectInputs
    outputs: DirectoryOutputs


class SummarizeClassStatistics(BaseModel):
    identifier: Literal["summarize-class-statistics"] = "summarize-class-statistics"
    inputs: DataDirInput
    outputs: DirectoryOutputs


TWorkflowStep = Union[
    DatasetQueryStep,
    NDVIStep,
    EVIStep,
    NDWIStep,
    SAVIStep,
    ClipStep,
    ReprojectStep,
    SummarizeClassStatistics,
]
