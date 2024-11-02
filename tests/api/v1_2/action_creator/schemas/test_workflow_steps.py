from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from src.api.v1_2.action_creator.schemas.workflow_steps import (
    EPSG_CODES,
    CDOMStep,
    ClipStep,
    CorineLandCoverDatasetQueryStep,
    CYAStep,
    DefraCalibrateStep,
    DOCStep,
    EVIStep,
    GlobalLandCoverDatasetQueryStep,
    NDVIStep,
    NDWIStep,
    ReprojectStep,
    SARWaterMask,
    SAVIStep,
    Sentinel1DatasetQueryStep,
    Sentinel2DatasetQueryStep,
    SummarizeClassStatisticsStep,
    WaterBodiesDatasetQueryStep,
    WorkflowStep,
)
from src.consts.geometries import HEATHROW_AOI, UK_AOI


@pytest.fixture
def dir_inputs() -> dict[str, Any]:
    return {"data_dir": {"type": "directory", "name": "data_dir"}}


@pytest.fixture
def dir_outputs() -> dict[str, dict[str, Any]]:
    return {"results": {"type": "directory", "name": "results"}}


@pytest.fixture
def inputs(dir_inputs: dict[str, Any], dir_outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "inputs": dir_inputs,
        "outputs": dir_outputs,
    }


@pytest.fixture
def query_step_inputs(dir_outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "inputs": {
            "stac_collection": "test",
            "area": HEATHROW_AOI,
            "date_start": "2000-01-01",
            "date_end": "2024-01-01",
            "limit": 23,
        },
        "outputs": dir_outputs,
    }


@pytest.mark.parametrize(
    "orbit_direction",
    [["ascending"], ["descending"], ["ascending", "descending"]],
)
@pytest.mark.parametrize(
    "polarization",
    [["VV"], ["VV", "VV+VH"], ["HH"], ["HH+HV"], ["HH", "HH+HV", "VV", "VV+VH"]],
)
def test_s1_query_step(query_step_inputs: dict[str, Any], orbit_direction: list[str], polarization: list[str]) -> None:
    # Arrange
    query_step_inputs["inputs"]["stac_collection"] = "sentinel-1-grd"
    query_step_inputs["inputs"]["date_start"] = "2023-01-01"
    query_step_inputs["inputs"]["orbit_direction"] = orbit_direction
    query_step_inputs["inputs"]["polarization"] = polarization

    # Act & Assert
    Sentinel1DatasetQueryStep(**query_step_inputs)


@pytest.mark.parametrize(
    "collection",
    [
        "sentinel-2-l1c",
        "sentinel-2-l2a",
        "sentinel-2-l2a-ard",
    ],
)
@pytest.mark.parametrize("cc_min", list(range(0, 101, 25)))
@pytest.mark.parametrize("cc_max", list(range(0, 101, 25)))
def test_s2_query_step(query_step_inputs: dict[str, Any], collection: str | None, cc_min: int, cc_max: int) -> None:
    # Arrange
    query_step_inputs["inputs"]["stac_collection"] = collection
    query_step_inputs["inputs"]["date_start"] = "2023-01-01"
    query_step_inputs["inputs"]["cloud_cover_min"] = cc_min
    query_step_inputs["inputs"]["cloud_cover_max"] = cc_max

    # Act & Assert
    if cc_min > cc_max:
        with pytest.raises(ValidationError):
            Sentinel2DatasetQueryStep(**query_step_inputs)
    else:
        Sentinel2DatasetQueryStep(**query_step_inputs)


def test_esa_glcm_query_step(query_step_inputs: dict[str, Any]) -> None:
    # Arrange
    query_step_inputs["inputs"]["stac_collection"] = "esa-lccci-glcm"
    query_step_inputs["inputs"]["date_start"] = "1992-01-01"
    query_step_inputs["inputs"]["date_end"] = "2015-12-31"

    # Act & Assert
    GlobalLandCoverDatasetQueryStep(**query_step_inputs)


def test_corine_query_step(query_step_inputs: dict[str, Any]) -> None:
    # Arrange
    query_step_inputs["inputs"]["stac_collection"] = "clms-corine-lc"
    query_step_inputs["inputs"]["date_start"] = "1992-01-01"
    query_step_inputs["inputs"]["date_end"] = "2015-12-31"

    # Act & Assert
    CorineLandCoverDatasetQueryStep(**query_step_inputs)


def test_water_bodies_query_step(query_step_inputs: dict[str, Any]) -> None:
    # Arrange
    query_step_inputs["inputs"]["stac_collection"] = "clms-water-bodies"
    query_step_inputs["inputs"]["date_start"] = "2020-01-01"
    query_step_inputs["inputs"]["date_end"] = "2023-12-31"

    # Act & Assert
    WaterBodiesDatasetQueryStep(**query_step_inputs)


@pytest.mark.parametrize(
    ("cls", "collection", "date_start", "date_end", "area", "match"),
    [
        (
            Sentinel1DatasetQueryStep,
            "sentinel-1-grd",
            "2023-01-01",
            "2022-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            Sentinel1DatasetQueryStep,
            "sentinel-1-grd",
            "2023-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            Sentinel2DatasetQueryStep,
            "sentinel-2-l2a",
            "2023-01-01",
            "2022-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            Sentinel2DatasetQueryStep,
            "sentinel-1-grd",
            "2023-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            GlobalLandCoverDatasetQueryStep,
            "esa-lccci-glcm",
            "2012-01-01",
            "2010-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            GlobalLandCoverDatasetQueryStep,
            "sentinel-1-grd",
            "2006-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            CorineLandCoverDatasetQueryStep,
            "clms-corine-lc",
            "2012-01-01",
            "2010-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            CorineLandCoverDatasetQueryStep,
            "clms-corine-lc",
            "2008-01-01",
            "2015-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            WaterBodiesDatasetQueryStep,
            "clms-water-bodies",
            "2022-01-01",
            "2021-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            WaterBodiesDatasetQueryStep,
            "sentinel-1-grd",
            "2023-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
    ],
)
def test_dataset_query_step_should_raise(
    query_step_inputs: dict[str, Any],
    cls: type[WorkflowStep],
    collection: str,
    date_start: str,
    date_end: str,
    area: dict[str, Any],
    match: str,
) -> None:
    # Arrange
    query_step_inputs["inputs"]["stac_collection"] = collection
    query_step_inputs["inputs"]["date_start"] = date_start
    query_step_inputs["inputs"]["date_end"] = date_end
    query_step_inputs["inputs"]["area"] = area

    # Act & Assert
    with pytest.raises(ValidationError, match=match):
        cls(**query_step_inputs)


@pytest.mark.parametrize(
    "cls",
    [
        NDVIStep,
        EVIStep,
        NDWIStep,
        SAVIStep,
        CYAStep,
        CDOMStep,
        DOCStep,
        SARWaterMask,
    ],
)
def test_index_calculation_step(inputs: dict[str, Any], cls: type[WorkflowStep]) -> None:
    # Act & Assert
    cls(**inputs)


def test_summarize_classes_step(inputs: dict[str, Any]) -> None:
    # Act & Assert
    SummarizeClassStatisticsStep(**inputs)


def test_defra_calibration_step(inputs: dict[str, Any]) -> None:
    # Act & Assert
    DefraCalibrateStep(**inputs)


def test_clip_step(inputs: dict[str, Any]) -> None:
    # Arrange
    inputs["identifier"] = "clip"
    inputs["inputs"]["aoi"] = HEATHROW_AOI

    # Assert
    ClipStep(**inputs)


def test_clip_step_raises_on_large_area(inputs: dict[str, Any]) -> None:
    # Arrange
    inputs["identifier"] = "clip"
    inputs["inputs"]["aoi"] = UK_AOI

    # Act & Assert
    with pytest.raises(ValidationError, match="Area exceeds"):
        ClipStep(**inputs)


@pytest.mark.parametrize(
    ("epsg_codes", "should_raise"),
    [(EPSG_CODES, False), (["EPSG:0000"], True)],
    ids=["all_proj_codes", "invalid_epsg_code"],
)
def test_reproject_step(epsg_codes: list[str], should_raise: bool, inputs: dict[str, Any]) -> None:  # noqa: FBT001
    # Arrange
    inputs["identifier"] = "reproject"

    # Act & Assert
    for code in epsg_codes:
        inputs["inputs"]["epsg"] = code
        if should_raise:
            with pytest.raises(ValidationError):
                ReprojectStep(**inputs)
        else:
            ReprojectStep(**inputs)
