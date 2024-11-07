from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from src.api.v1_2.action_creator.schemas.workflow_tasks import (
    EPSG_CODES,
    CDOMTask,
    ClipTask,
    CorineLandCoverDatasetQueryTask,
    CYATask,
    DefraCalibrateTask,
    DOCTask,
    EVITask,
    GlobalLandCoverDatasetQueryTask,
    NDVITask,
    NDWITask,
    ReprojectTask,
    SARWaterMask,
    SAVITask,
    Sentinel1DatasetQueryTask,
    Sentinel2DatasetQueryTask,
    SummarizeClassStatisticsTask,
    WaterBodiesDatasetQueryTask,
    WorkflowTask,
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
def query_task_inputs(dir_outputs: dict[str, Any]) -> dict[str, Any]:
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
def test_s1_query_task(query_task_inputs: dict[str, Any], orbit_direction: list[str], polarization: list[str]) -> None:
    # Arrange
    query_task_inputs["inputs"]["stac_collection"] = "sentinel-1-grd"
    query_task_inputs["inputs"]["date_start"] = "2023-01-01"
    query_task_inputs["inputs"]["orbit_direction"] = orbit_direction
    query_task_inputs["inputs"]["polarization"] = polarization

    # Act & Assert
    Sentinel1DatasetQueryTask(**query_task_inputs)


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
def test_s2_query_task(query_task_inputs: dict[str, Any], collection: str | None, cc_min: int, cc_max: int) -> None:
    # Arrange
    query_task_inputs["inputs"]["stac_collection"] = collection
    query_task_inputs["inputs"]["date_start"] = "2023-01-01"
    query_task_inputs["inputs"]["cloud_cover_min"] = cc_min
    query_task_inputs["inputs"]["cloud_cover_max"] = cc_max

    # Act & Assert
    if cc_min > cc_max:
        with pytest.raises(ValidationError):
            Sentinel2DatasetQueryTask(**query_task_inputs)
    else:
        Sentinel2DatasetQueryTask(**query_task_inputs)


def test_esa_glcm_query_task(query_task_inputs: dict[str, Any]) -> None:
    # Arrange
    query_task_inputs["inputs"]["stac_collection"] = "esa-lccci-glcm"
    query_task_inputs["inputs"]["date_start"] = "1992-01-01"
    query_task_inputs["inputs"]["date_end"] = "2015-12-31"

    # Act & Assert
    GlobalLandCoverDatasetQueryTask(**query_task_inputs)


def test_corine_query_task(query_task_inputs: dict[str, Any]) -> None:
    # Arrange
    query_task_inputs["inputs"]["stac_collection"] = "clms-corine-lc"
    query_task_inputs["inputs"]["date_start"] = "1992-01-01"
    query_task_inputs["inputs"]["date_end"] = "2015-12-31"

    # Act & Assert
    CorineLandCoverDatasetQueryTask(**query_task_inputs)


def test_water_bodies_query_task(query_task_inputs: dict[str, Any]) -> None:
    # Arrange
    query_task_inputs["inputs"]["stac_collection"] = "clms-water-bodies"
    query_task_inputs["inputs"]["date_start"] = "2020-01-01"
    query_task_inputs["inputs"]["date_end"] = "2023-12-31"

    # Act & Assert
    WaterBodiesDatasetQueryTask(**query_task_inputs)


@pytest.mark.parametrize(
    ("cls", "collection", "date_start", "date_end", "area", "match"),
    [
        (
            Sentinel1DatasetQueryTask,
            "sentinel-1-grd",
            "2023-01-01",
            "2022-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            Sentinel1DatasetQueryTask,
            "sentinel-1-grd",
            "2023-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            Sentinel2DatasetQueryTask,
            "sentinel-2-l2a",
            "2023-01-01",
            "2022-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            Sentinel2DatasetQueryTask,
            "sentinel-1-grd",
            "2023-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            GlobalLandCoverDatasetQueryTask,
            "esa-lccci-glcm",
            "2012-01-01",
            "2010-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            GlobalLandCoverDatasetQueryTask,
            "sentinel-1-grd",
            "2006-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            CorineLandCoverDatasetQueryTask,
            "clms-corine-lc",
            "2012-01-01",
            "2010-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            CorineLandCoverDatasetQueryTask,
            "clms-corine-lc",
            "2008-01-01",
            "2015-01-01",
            UK_AOI,
            "Area exceeds",
        ),
        (
            WaterBodiesDatasetQueryTask,
            "clms-water-bodies",
            "2022-01-01",
            "2021-01-01",
            HEATHROW_AOI,
            "End date cannot be before start date",
        ),
        (
            WaterBodiesDatasetQueryTask,
            "sentinel-1-grd",
            "2023-01-01",
            "2024-01-01",
            UK_AOI,
            "Area exceeds",
        ),
    ],
)
def test_dataset_query_task_should_raise(
    query_task_inputs: dict[str, Any],
    cls: type[WorkflowTask],
    collection: str,
    date_start: str,
    date_end: str,
    area: dict[str, Any],
    match: str,
) -> None:
    # Arrange
    query_task_inputs["inputs"]["stac_collection"] = collection
    query_task_inputs["inputs"]["date_start"] = date_start
    query_task_inputs["inputs"]["date_end"] = date_end
    query_task_inputs["inputs"]["area"] = area

    # Act & Assert
    with pytest.raises(ValidationError, match=match):
        cls(**query_task_inputs)


@pytest.mark.parametrize(
    "cls",
    [
        NDVITask,
        EVITask,
        NDWITask,
        SAVITask,
        CYATask,
        CDOMTask,
        DOCTask,
        SARWaterMask,
    ],
)
def test_index_calculation_task(inputs: dict[str, Any], cls: type[WorkflowTask]) -> None:
    # Act & Assert
    cls(**inputs)


def test_summarize_classes_task(inputs: dict[str, Any]) -> None:
    # Act & Assert
    SummarizeClassStatisticsTask(**inputs)


def test_defra_calibration_task(inputs: dict[str, Any]) -> None:
    # Act & Assert
    DefraCalibrateTask(**inputs)


def test_clip_task(inputs: dict[str, Any]) -> None:
    # Arrange
    inputs["identifier"] = "clip"
    inputs["inputs"]["aoi"] = HEATHROW_AOI

    # Assert
    ClipTask(**inputs)


def test_clip_task_raises_on_large_area(inputs: dict[str, Any]) -> None:
    # Arrange
    inputs["identifier"] = "clip"
    inputs["inputs"]["aoi"] = UK_AOI

    # Act & Assert
    with pytest.raises(ValidationError, match="Area exceeds"):
        ClipTask(**inputs)


@pytest.mark.parametrize(
    ("epsg_codes", "should_raise"),
    [(EPSG_CODES, False), (["EPSG:0000"], True)],
    ids=["all_proj_codes", "invalid_epsg_code"],
)
def test_reproject_task(epsg_codes: list[str], should_raise: bool, inputs: dict[str, Any]) -> None:  # noqa: FBT001
    # Arrange
    inputs["identifier"] = "reproject"

    # Act & Assert
    for code in epsg_codes:
        inputs["inputs"]["epsg"] = code
        if should_raise:
            with pytest.raises(ValidationError):
                ReprojectTask(**inputs)
        else:
            ReprojectTask(**inputs)
