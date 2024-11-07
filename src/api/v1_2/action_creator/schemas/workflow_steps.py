from __future__ import annotations

import abc
import functools
from datetime import datetime
from enum import StrEnum, auto
from typing import Annotated, Any, Literal, Union

import pandas as pd
from geojson_pydantic import Polygon
from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo
from pyproj.database import query_crs_info

from src import consts
from src.api.v1_2.action_creator.schemas.functions import (
    ConstraintOperator,
    FuncInputOutputType,
    FunctionCategory,
    FunctionInputConstraint,
    FunctionInputOption,
    FunctionOutputType,
)
from src.services.validation_utils import ensure_area_smaller_than, validate_date_range


def get_crs_list() -> list[str]:
    crs_info_list = query_crs_info(auth_name=None, pj_types=None)
    crs_list = [f"EPSG:{info[1]}" for info in crs_info_list]
    return sorted(crs_list)


EPSG_CODES = get_crs_list()


class ValueType(StrEnum):
    ref = auto()
    atom = auto()


class InputOutputValue(BaseModel):
    type: ValueType = Field(ValueType.atom, alias="$type")
    value: Any | None = None


class StepOutputSpec(BaseModel):
    name: str
    type: FunctionOutputType


class OrbitDirection(StrEnum):
    ascending = auto()
    descending = auto()


class Polarization(StrEnum):
    vv = "VV"
    vv_vh = "VV+VH"
    hh = "HH"
    hh_hv = "HH+HV"


class DirectoryStepOutputSpec(BaseModel):
    type: Literal["directory"] = "directory"
    name: Literal["results"] = "results"


class DirectoryOutputs(BaseModel):
    results: DirectoryStepOutputSpec


class WorkflowStep(BaseModel, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def as_function_spec(cls) -> dict[str, Any]: ...


class QueryStepInputsBase(BaseModel):
    stac_collection: str
    area: Polygon
    date_start: datetime | None
    date_end: datetime | None

    @field_validator("area", mode="after")
    @classmethod
    def validate_area(cls, v: Polygon) -> Polygon:
        ensure_area_smaller_than(v.model_dump(mode="json"))
        return v

    @field_validator("date_end", mode="after")
    @classmethod
    def validate_date_range(cls, v: datetime | None, info: ValidationInfo) -> datetime | None:
        start_date = info.data.get("date_start")
        validate_date_range(start_date, v)
        return v


class Sentinel1QueryStepInputs(QueryStepInputsBase):
    stac_collection: Literal["sentinel-1-grd"] = "sentinel-1-grd"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="2014-10-10")]
    date_end: datetime | None
    orbit_direction: list[OrbitDirection] = Field(default_factory=list)
    polarization: list[Polarization] = Field(default_factory=list)
    limit: int | None = 10


class Sentinel1DatasetQueryStep(WorkflowStep):
    identifier: Literal["s1-ds-query"] = "s1-ds-query"
    inputs: Sentinel1QueryStepInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "Sentinel-1 Dataset Query",
            "identifier": "s1-ds-query",
            "category": FunctionCategory.data_select,
            "tags": ["Sentinel-1", "Satellite"],
            "description": "Query Sentinel-1 dataset.",
            "visible": False,
            "compatible_input_datasets": ["sentinel-1-grd"],
            "inputs": {
                "stac_collection": {
                    "name": "stac_collection",
                    "description": "STAC Collection identifier for Sentinel-1",
                    "type": FuncInputOutputType.string,
                    "required": True,
                    "default": "sentinel-1-grd",
                },
                "area": {
                    "name": "area",
                    "description": "Area of interest as a polygon",
                    "type": FuncInputOutputType.polygon,
                    "required": True,
                },
                "date_start": {
                    "name": "date_start",
                    "description": "Start date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [FunctionInputConstraint(operator=ConstraintOperator.ge, value="2014-10-10")],
                },
                "date_end": {
                    "name": "date_end",
                    "description": "End date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                },
                "orbit_direction": {
                    "name": "orbit_direction",
                    "description": "Orbit direction options",
                    "type": FuncInputOutputType.string,
                    "options": [FunctionInputOption(label=i.capitalize(), value=i) for i in OrbitDirection],
                    "required": True,
                },
                "polarization": {
                    "name": "polarization",
                    "description": "Polarization options",
                    "type": FuncInputOutputType.string,
                    "options": [FunctionInputOption(label=i.upper(), value=i) for i in Polarization],
                    "required": True,
                },
                "limit": {
                    "name": "limit",
                    "description": "Limit for number of results",
                    "type": FuncInputOutputType.number,
                    "required": False,
                    "default": 10,
                },
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store query results",
                }
            },
        }


class Sentinel2QueryStepInputs(QueryStepInputsBase):
    stac_collection: Literal["sentinel-2-l1c", "sentinel-2-l2a", "sentinel-2-l2a-ard"] = "sentinel-2-l2a-ard"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="2015-06-27")]
    date_end: datetime | None
    cloud_cover_min: Annotated[int, Field(default=0, ge=0, le=100)]
    cloud_cover_max: Annotated[int, Field(default=100, ge=0, le=100)]
    limit: int | None = 10

    @field_validator("cloud_cover_max", mode="after")
    @classmethod
    def validate_cc_range(cls, cloud_cover_max: int, info: ValidationInfo) -> int:
        cloud_cover_min = info.data.get("cloud_cover_min")
        if cloud_cover_min > cloud_cover_max:
            msg = "Min cloud cover cannot be greater than max cloud cover"
            raise ValueError(msg)
        return cloud_cover_max


class Sentinel2DatasetQueryStep(WorkflowStep):
    identifier: Literal["s2-ds-query"] = "s2-ds-query"
    inputs: Sentinel2QueryStepInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "Sentinel-2 Dataset Query",
            "identifier": "s2-ds-query",
            "category": FunctionCategory.data_select,
            "tags": ["Sentinel-2", "Satellite"],
            "description": "Query Sentinel-2 datasets.",
            "visible": True,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a", "sentinel-2-l2a-ard"],
            "inputs": {
                "stac_collection": {
                    "name": "stac_collection",
                    "description": "STAC Collection identifier for Sentinel-2",
                    "type": FuncInputOutputType.string,
                    "required": True,
                    "options": [
                        FunctionInputOption(label="Sentinel-2 L1C", value="sentinel-2-l1c"),
                        FunctionInputOption(label="Sentinel-2 L2A", value="sentinel-2-l2a"),
                        FunctionInputOption(label="Sentinel-2 L2A ARD", value="sentinel-2-l2a-ard"),
                    ],
                    "default": "sentinel-2-l2a-ard",
                },
                "area": {
                    "name": "area",
                    "description": "Area of interest as a polygon",
                    "type": FuncInputOutputType.polygon,
                    "required": True,
                },
                "date_start": {
                    "name": "date_start",
                    "description": "Start date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [FunctionInputConstraint(operator=ConstraintOperator.ge, value="2015-06-27")],
                },
                "date_end": {
                    "name": "date_end",
                    "description": "End date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                },
                "cloud_cover_min": {
                    "name": "cloud_cover_min",
                    "description": "Minimum cloud cover percentage",
                    "type": FuncInputOutputType.number,
                    "required": False,
                    "default": 0,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value=0),
                        FunctionInputConstraint(operator=ConstraintOperator.le, value=100),
                    ],
                },
                "cloud_cover_max": {
                    "name": "cloud_cover_max",
                    "description": "Maximum cloud cover percentage",
                    "type": FuncInputOutputType.number,
                    "required": False,
                    "default": 100,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value=0),
                        FunctionInputConstraint(operator=ConstraintOperator.le, value=100),
                    ],
                },
                "limit": {
                    "name": "limit",
                    "description": "Limit for number of results",
                    "type": FuncInputOutputType.number,
                    "required": False,
                    "default": 10,
                },
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store query results",
                }
            },
        }


class GlobalLandCoverQueryStepInputs(QueryStepInputsBase):
    stac_collection: Literal["esa-lccci-glcm"] = "esa-lccci-glcm"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="1992-01-01T00:00:00", le="2015-12-31T23:59:59")]
    date_end: Annotated[datetime | None, Field(None, ge="1992-01-01T00:00:00", le="2015-12-31T23:59:59")]
    limit: int | None = 10


class GlobalLandCoverDatasetQueryStep(WorkflowStep):
    identifier: Literal["esa-glc-ds-query"] = "esa-glc-ds-query"
    inputs: GlobalLandCoverQueryStepInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "ESA Global Land Cover Dataset Query",
            "identifier": "esa-glc-ds-query",
            "category": FunctionCategory.data_select,
            "tags": ["Global Land Cover", "ESA"],
            "description": "Query ESA Global Land Cover datasets.",
            "visible": True,
            "compatible_input_datasets": ["esa-lccci-glcm"],
            "inputs": {
                "stac_collection": {
                    "name": "stac_collection",
                    "description": "STAC Collection identifier for ESA Global Land Cover",
                    "type": FuncInputOutputType.string,
                    "required": True,
                    "default": "esa-lccci-glcm",
                    "options": [FunctionInputOption(label="ESA Land Cover CCI", value="esa-lccci-glcm")],
                },
                "area": {
                    "name": "area",
                    "description": "Area of interest as a polygon",
                    "type": FuncInputOutputType.polygon,
                    "required": True,
                },
                "date_start": {
                    "name": "date_start",
                    "description": "Start date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value="1992-01-01T00:00:00"),
                        FunctionInputConstraint(operator=ConstraintOperator.le, value="2015-12-31T23:59:59"),
                    ],
                },
                "date_end": {
                    "name": "date_end",
                    "description": "End date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value="1992-01-01T00:00:00"),
                        FunctionInputConstraint(operator=ConstraintOperator.le, value="2015-12-31T23:59:59"),
                    ],
                },
                "limit": {
                    "name": "limit",
                    "description": "Limit for number of results",
                    "type": FuncInputOutputType.number,
                    "required": False,
                    "default": 10,
                },
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store query results",
                }
            },
        }


class CorineLandCoverQueryStepInputs(QueryStepInputsBase):
    stac_collection: Literal["clms-corine-lc"] = "clms-corine-lc"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="1990-01-01T00:00:00", le="2018-12-31T23:59:59")]
    date_end: Annotated[datetime | None, Field(None, ge="1990-01-01T00:00:00", le="2018-12-31T23:59:59")]
    limit: int | None = 10


class CorineLandCoverDatasetQueryStep(WorkflowStep):
    identifier: Literal["corine-lc-ds-query"] = "corine-lc-ds-query"
    inputs: CorineLandCoverQueryStepInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "Corine Land Cover Dataset Query",
            "identifier": "corine-lc-ds-query",
            "category": FunctionCategory.data_select,
            "tags": ["Land Cover", "Corine Land Cover", "CLC"],
            "description": "Query Corine Land Cover datasets with constraints on temporal range.",
            "visible": True,
            "compatible_input_datasets": ["clms-corine-lc"],
            "inputs": {
                "stac_collection": {
                    "name": "stac_collection",
                    "description": "STAC Collection identifier for Corine Land Cover",
                    "type": FuncInputOutputType.string,
                    "required": True,
                    "default": "clms-corine-lc",
                    "options": [FunctionInputOption(label="Corine Land Cover", value="clms-corine-lc")],
                },
                "area": {
                    "name": "area",
                    "description": "Area of interest as a polygon",
                    "type": FuncInputOutputType.polygon,
                    "required": True,
                },
                "date_start": {
                    "name": "date_start",
                    "description": "Start date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value="1990-01-01T00:00:00"),
                        FunctionInputConstraint(operator=ConstraintOperator.le, value="2018-12-31T23:59:59"),
                    ],
                },
                "date_end": {
                    "name": "date_end",
                    "description": "End date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value="1990-01-01T00:00:00"),
                        FunctionInputConstraint(operator=ConstraintOperator.le, value="2018-12-31T23:59:59"),
                    ],
                },
                "limit": {
                    "name": "limit",
                    "description": "Limit for number of results",
                    "type": FuncInputOutputType.number,
                    "required": False,
                    "default": 10,
                },
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store query results",
                }
            },
        }


class WaterBodiesQueryStepInputs(QueryStepInputsBase):
    stac_collection: Literal["clms-water-bodies"] = "clms-water-bodies"
    area: Polygon
    date_start: Annotated[datetime | None, Field(None, ge="2020-01-01T00:00:00")]
    date_end: Annotated[datetime | None, Field(None, ge="2020-01-01T00:00:00")]
    limit: int | None = 10


class WaterBodiesDatasetQueryStep(WorkflowStep):
    identifier: Literal["water-bodies-ds-query"] = "water-bodies-ds-query"
    inputs: WaterBodiesQueryStepInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "Water Bodies Dataset Query",
            "identifier": "water-bodies-ds-query",
            "category": FunctionCategory.data_select,
            "tags": ["Land Cover", "Water Bodies", "CLMS"],
            "description": "Query Water Bodies datasets.",
            "visible": True,
            "compatible_input_datasets": ["clms-water-bodies"],
            "inputs": {
                "stac_collection": {
                    "name": "stac_collection",
                    "description": "STAC Collection identifier for CLMS Water Bodies",
                    "type": FuncInputOutputType.string,
                    "required": True,
                    "default": "clms-water-bodies",
                    "options": [FunctionInputOption(label="CLMS Water Bodies", value="clms-water-bodies")],
                },
                "area": {
                    "name": "area",
                    "description": "Area of interest as a polygon",
                    "type": FuncInputOutputType.polygon,
                    "required": True,
                },
                "date_start": {
                    "name": "date_start",
                    "description": "Start date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value="2020-01-01T00:00:00")
                    ],
                },
                "date_end": {
                    "name": "date_end",
                    "description": "End date for the data query",
                    "type": FuncInputOutputType.datetime,
                    "required": False,
                    "constraints": [
                        FunctionInputConstraint(operator=ConstraintOperator.ge, value="2020-01-01T00:00:00")
                    ],
                },
                "limit": {
                    "name": "limit",
                    "description": "Limit for number of results",
                    "type": FuncInputOutputType.number,
                    "required": False,
                    "default": 10,
                },
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store query results",
                }
            },
        }


class DataDirInput(BaseModel):
    name: Literal["data_dir", "results"] = "data_dir"
    type: Literal["directory"] = "directory"


class DirectoryInputs(BaseModel):
    data_dir: DataDirInput


class NDVIStep(WorkflowStep):
    identifier: Literal["ndvi"] = "ndvi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "NDVI Calculation",
            "identifier": "ndvi",
            "category": FunctionCategory.spectral_indices,
            "tags": ["NDVI", "Vegetation Index", "Spectral indices"],
            "description": "Calculate Normalized Difference Vegetation Index (NDVI).",
            "visible": True,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store index calculation results",
                }
            },
        }


class EVIStep(WorkflowStep):
    identifier: Literal["evi"] = "evi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "EVI Calculation",
            "identifier": "evi",
            "category": FunctionCategory.spectral_indices,
            "tags": ["EVI", "Vegetation Index", "Spectral indices"],
            "description": "Calculate Enhanced Vegetation Index (EVI).",
            "visible": True,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store index calculation results",
                }
            },
        }


class SAVIStep(WorkflowStep):
    identifier: Literal["savi"] = "savi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "SAVI Calculation",
            "identifier": "savi",
            "category": FunctionCategory.spectral_indices,
            "tags": ["SAVI", "Vegetation Index", "Spectral indices"],
            "description": "Soil Adjusted Vegetation Index (SAVI).",
            "visible": True,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store index calculation results",
                }
            },
        }


class NDWIStep(WorkflowStep):
    identifier: Literal["ndwi"] = "ndwi"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "NDWI",
            "identifier": "ndwi",
            "category": FunctionCategory.spectral_indices,
            "tags": ["NDWI", "Water Index", "Spectral indices"],
            "description": "Normalized Difference Water Index (NDWI).",
            "visible": False,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store index calculation results",
                }
            },
        }


class CYAStep(WorkflowStep):
    identifier: Literal["cya"] = "cya"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "CYA Calculation",
            "identifier": "cya",
            "category": FunctionCategory.spectral_indices,
            "tags": ["CYA", "Water Quality", "Spectral indices"],
            "description": "Cyanobacteria Density Index (CYA).",
            "visible": False,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store index calculation results",
                }
            },
        }


class CDOMStep(WorkflowStep):
    identifier: Literal["cdom"] = "cdom"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "CDOM",
            "identifier": "cdom",
            "category": FunctionCategory.spectral_indices,
            "tags": ["CDOM", "Water Quality"],
            "description": "Colored Dissolved Organic Matter Index (CDOM).",
            "visible": False,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store index calculation results",
                }
            },
        }


class DOCStep(WorkflowStep):
    identifier: Literal["doc"] = "doc"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "DOC",
            "identifier": "doc",
            "category": FunctionCategory.spectral_indices,
            "tags": ["DOC", "Water Quality"],
            "description": "Dissolved Organic Carbon Index (DOC).",
            "visible": False,
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store index calculation results",
                }
            },
        }


class SARWaterMask(WorkflowStep):
    identifier: Literal["sar-water-mask"] = "sar-water-mask"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "SAR Water Mask",
            "identifier": "sar-water-mask",
            "category": FunctionCategory.spectral_indices,
            "tags": ["SAR", "Water Quality"],
            "description": "Water Mask generation using SAR data.",
            "visible": False,
            "compatible_input_datasets": ["sentinel-1-grd"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store calculation results",
                }
            },
        }


class ClipInputs(BaseModel):
    data_dir: DataDirInput
    aoi: Polygon

    @field_validator("aoi", mode="after")
    @classmethod
    def validate_aoi(cls, v: Polygon) -> Polygon:
        ensure_area_smaller_than(v.model_dump(mode="json"))
        return v


class ClipStep(WorkflowStep):
    identifier: Literal["clip"] = "clip"
    inputs: ClipInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "Clip Operation",
            "identifier": "clip",
            "category": FunctionCategory.raster_ops,
            "tags": ["Clip", "AOI"],
            "description": "Perform a clip operation on the input data using a specified area of interest (AOI).",
            "visible": True,
            "compatible_input_datasets": [
                "sentinel-1-grd",
                "sentinel-2-l1c",
                "sentinel-2-l2a",
                "esa-lccci-glcm",
                "clms-corine-lc",
                "clms-water-bodies",
            ],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data to be clipped",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                },
                "aoi": {
                    "name": "aoi",
                    "description": "Area of interest for clipping, specified as a polygon",
                    "type": FuncInputOutputType.polygon,
                    "required": True,
                },
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store the results of the clip operation",
                }
            },
        }


class ReprojectInputs(BaseModel):
    data_dir: DataDirInput
    epsg: Literal[*EPSG_CODES] = "EPSG:4326"  # type: ignore[valid-type]


class ReprojectStep(WorkflowStep):
    identifier: Literal["reproject"] = "reproject"
    inputs: ReprojectInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "Reproject Operation",
            "identifier": "reproject",
            "category": FunctionCategory.raster_ops,
            "tags": ["Reproject", "CRS", "EPSG"],
            "description": "Reproject data to a specified EPSG coordinate reference system (CRS).",
            "visible": True,
            "compatible_input_datasets": [
                "sentinel-1-grd",
                "sentinel-2-l1c",
                "sentinel-2-l2a",
                "sentinel-2-l2a-ard",
                "esa-lccci-glcm",
                "clms-corine-lc",
                "clms-water-bodies",
            ],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data to be reprojected",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                },
                "epsg": {
                    "name": "epsg",
                    "description": "EPSG code of the target coordinate reference system (CRS) for reprojection",
                    "type": FuncInputOutputType.string,
                    "required": True,
                    "options": [FunctionInputOption(label=code, value=code) for code in ["EPSG:4326", "EPSG:3857"]],
                },
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store the reprojected data",
                }
            },
        }


class SummarizeClassStatisticsStep(WorkflowStep):
    identifier: Literal["summarize-class-statistics"] = "summarize-class-statistics"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "Summarize Class Statistics",
            "identifier": "summarize-class-statistics",
            "category": FunctionCategory.raster_ops,
            "tags": ["Class Statistics", "Summarize", "Pixel Classification"],
            "description": "Generate summary statistics for classified raster data, such as class counts "
            "and area proportions.",
            "visible": True,
            "compatible_input_datasets": ["esa-lccci-glcm", "clms-corine-lc", "clms-water-bodies"],
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the classified raster data",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store the summarized class statistics",
                }
            },
        }


class DefraCalibrateStep(WorkflowStep):
    identifier: Literal["defra-calibrate"] = "defra-calibrate"
    inputs: DirectoryInputs
    outputs: DirectoryOutputs

    @classmethod
    def as_function_spec(cls) -> dict[str, Any]:
        return {
            "name": "DEFRA Calibration",
            "identifier": "defra-calibrate",
            "category": FunctionCategory.other,
            "tags": ["DEFRA", "Calibration", "Water Quality"],
            "description": "Calibrate input data based on DEFRA in-situ data.",
            "compatible_input_datasets": ["sentinel-2-l1c", "sentinel-2-l2a"],
            "visible": False,
            "inputs": {
                "data_dir": {
                    "name": "data_dir",
                    "description": "Directory containing the input data for DEFRA calibration",
                    "type": FuncInputOutputType.directory,
                    "required": True,
                }
            },
            "outputs": {
                "results": {
                    "name": "results",
                    "type": FuncInputOutputType.directory,
                    "description": "Directory to store the DEFRA-calibrated data",
                }
            },
        }


class WorkflowValidationResult(BaseModel):
    valid: bool


WORKFLOW_STEPS = [
    # DS Queries
    Sentinel1DatasetQueryStep,
    Sentinel2DatasetQueryStep,
    GlobalLandCoverDatasetQueryStep,
    CorineLandCoverDatasetQueryStep,
    WaterBodiesDatasetQueryStep,
    # Indices
    NDVIStep,
    EVIStep,
    NDWIStep,
    SAVIStep,
    CYAStep,
    CDOMStep,
    DOCStep,
    SARWaterMask,
    # Raster ops
    ClipStep,
    ReprojectStep,
    # Water quality
    DefraCalibrateStep,
    # Pixel classification
    SummarizeClassStatisticsStep,
]

TWorkflowStep = Annotated[Union[*WORKFLOW_STEPS], Field(discriminator="identifier")]  # type: ignore[valid-type]
FUNCTIONS = [s.as_function_spec() for s in WORKFLOW_STEPS]
FUNCTIONS_REGISTRY = {f["identifier"]: f for f in FUNCTIONS}


class StepCompatibility(StrEnum):
    yes = auto()
    no = auto()
    maybe = auto()


def is_query_step(s: str) -> bool:
    return "ds-query" in s


def is_raster_ops_step(s: str) -> bool:
    return s in [f["identifier"] for f in FUNCTIONS if f["category"] == "raster_ops"]


@functools.cache
def load_step_compatibility_matrix() -> pd.DataFrame:
    return pd.read_csv(consts.directories.ASSETS_DIR / "wf-step-compatibility-matrix.csv", index_col=0, header=0)


def check_step_compatibility(s1: str, s2: str) -> StepCompatibility:
    """Checks whether Workflow Steps ``s1`` and ``s2`` are compatible with each other.

    i.e. if output of ``s1`` can be used as an input for ``s2``.

    Arguments:
        s1: The identifier of first function step.
        s2: The identifier of second function step.

    Returns:
        Compatibility flag.
        If result is ``maybe`` then additional checks with previous steps in the WF are required.
    """
    # Load compatibility matrix and get results from it
    return load_step_compatibility_matrix().loc[s1, s2]
