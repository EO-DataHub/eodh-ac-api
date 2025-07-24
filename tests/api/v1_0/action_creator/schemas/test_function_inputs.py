from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
from geojson_pydantic import Polygon
from pydantic_core import ValidationError

from src.api.v1_0.action_creator.schemas import (
    CommonPresetFunctionInputs,
    LandCoverChangeDetectionFunctionInputs,
    RasterCalculatorFunctionInputs,
    RasterCalculatorIndex,
    WaterQualityFunctionInputs,
    WaterQualityIndex,
)
from src.consts.action_creator import FUNCTIONS_REGISTRY
from src.consts.geometries import UK_AOI

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest


@pytest.mark.parametrize(
    "input_model_fixture,model_cls",  # noqa: PT006
    [
        ("raster_calculator_request_body", RasterCalculatorFunctionInputs),
        ("lulc_change_request_body", LandCoverChangeDetectionFunctionInputs),
        ("water_quality_request_body", WaterQualityFunctionInputs),
    ],
)
def test_defaults_for_common_params(
    input_model_fixture: str,
    model_cls: type[CommonPresetFunctionInputs],
    request: FixtureRequest,
) -> None:
    # Arrange
    inputs = request.getfixturevalue(input_model_fixture)
    identifier = inputs["preset_function"].pop("function_identifier")
    inputs = inputs["preset_function"].pop("inputs")
    inputs.pop("date_start")
    inputs.pop("date_end")
    inputs.pop("stac_collection")

    # Act
    result = model_cls(**inputs)

    # Assert
    assert result.date_end is None
    assert result.date_end is None
    assert result.aoi == Polygon(**inputs["aoi"])
    assert result.stac_collection == (FUNCTIONS_REGISTRY[identifier]["inputs"]["stac_collection"]["default"])


@pytest.mark.parametrize(
    "input_model_fixture,model_cls",  # noqa: PT006
    [
        ("raster_calculator_request_body", RasterCalculatorFunctionInputs),
        ("lulc_change_request_body", LandCoverChangeDetectionFunctionInputs),
        ("water_quality_request_body", WaterQualityFunctionInputs),
    ],
)
def test_raises_when_aoi_is_missing(
    input_model_fixture: str,
    model_cls: type[CommonPresetFunctionInputs],
    request: FixtureRequest,
) -> None:
    # Arrange
    inputs = request.getfixturevalue(input_model_fixture)["preset_function"]["inputs"]
    inputs.pop("aoi")

    # Act & Assert
    with pytest.raises(ValidationError, match=r"Area of Interest is missing."):
        model_cls(**inputs)


@pytest.mark.parametrize(
    "input_model_fixture,model_cls",  # noqa: PT006
    [
        ("raster_calculator_request_body", RasterCalculatorFunctionInputs),
        ("lulc_change_request_body", LandCoverChangeDetectionFunctionInputs),
        ("water_quality_request_body", WaterQualityFunctionInputs),
    ],
)
def test_raises_when_aoi_too_big(
    input_model_fixture: str,
    model_cls: type[CommonPresetFunctionInputs],
    request: FixtureRequest,
) -> None:
    # Arrange
    inputs = request.getfixturevalue(input_model_fixture)["preset_function"]["inputs"]
    inputs["aoi"] = UK_AOI

    # Act & Assert
    with pytest.raises(ValidationError, match="Area exceeds"):
        model_cls(**inputs)


@pytest.mark.parametrize(
    "input_model_fixture,model_cls",  # noqa: PT006
    [
        ("raster_calculator_request_body", RasterCalculatorFunctionInputs),
        ("lulc_change_request_body", LandCoverChangeDetectionFunctionInputs),
        ("water_quality_request_body", WaterQualityFunctionInputs),
    ],
)
def test_raises_when_invalid_date_range(
    input_model_fixture: str,
    model_cls: type[CommonPresetFunctionInputs],
    request: FixtureRequest,
) -> None:
    inputs = request.getfixturevalue(input_model_fixture)
    inputs["date_start"] = "2024-01-01"
    inputs["date_end"] = "2023-01-01"

    # Act & Assert
    with pytest.raises(ValidationError, match=r"End date cannot be before start date."):
        model_cls(**inputs)


@pytest.mark.parametrize(
    "input_model_fixture,model_cls",  # noqa: PT006
    [
        ("raster_calculator_request_body", RasterCalculatorFunctionInputs),
        ("lulc_change_request_body", LandCoverChangeDetectionFunctionInputs),
        ("water_quality_request_body", WaterQualityFunctionInputs),
    ],
)
def test_raises_when_invalid_stac_collection(
    input_model_fixture: str,
    model_cls: type[CommonPresetFunctionInputs],
    request: FixtureRequest,
) -> None:
    inputs = request.getfixturevalue(input_model_fixture)
    inputs["stac_collection"] = "invalid"

    # Act & Assert
    with pytest.raises(ValidationError, match="Collection 'invalid' cannot be used with"):
        model_cls(**inputs)


def test_default_index_for_raster_calculator(raster_calculator_request_body: dict[str, Any]) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"].pop("index")
    inputs = raster_calculator_request_body["preset_function"]["inputs"]

    # Act
    result = RasterCalculatorFunctionInputs(**inputs)

    # Assert
    assert result.index == RasterCalculatorIndex.NDVI


def test_default_limit_for_raster_calculator(raster_calculator_request_body: dict[str, Any]) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"].pop("limit")
    inputs = raster_calculator_request_body["preset_function"]["inputs"]

    # Act
    result = RasterCalculatorFunctionInputs(**inputs)

    # Assert
    assert result.limit == FUNCTIONS_REGISTRY["raster-calculate"]["inputs"]["limit"]["default"]


def test_default_index_for_water_quality(water_quality_request_body: dict[str, Any]) -> None:
    # Arrange
    water_quality_request_body["preset_function"]["inputs"].pop("index")
    inputs = water_quality_request_body["preset_function"]["inputs"]

    # Act
    result = WaterQualityFunctionInputs(**inputs)

    # Assert
    assert result.index == WaterQualityIndex.NDWI


def test_default_calibration_flag_water_quality(water_quality_request_body: dict[str, Any]) -> None:
    # Arrange
    water_quality_request_body["preset_function"]["inputs"].pop("calibrate")
    inputs = water_quality_request_body["preset_function"]["inputs"]

    # Act
    result = WaterQualityFunctionInputs(**inputs)

    # Assert
    assert not result.calibrate


def test_raster_calculator_as_ogc_process_inputs(raster_calculator_request_body: dict[str, Any]) -> None:
    # Arrange
    inputs = raster_calculator_request_body["preset_function"]["inputs"]
    model = RasterCalculatorFunctionInputs(**inputs)

    # Act
    result = model.as_ogc_process_inputs()

    # Assert
    assert result["stac_collection"] == inputs["stac_collection"]
    assert json.loads(result["aoi"]) == inputs["aoi"]
    assert result["date_start"] == inputs["date_start"]
    assert result["date_end"] == inputs["date_end"]
    assert result["index"] == inputs["index"]
    assert result["limit"] == inputs["limit"]


def test_lulc_change_as_ogc_process_inputs(lulc_change_request_body: dict[str, Any]) -> None:
    # Arrange
    inputs = lulc_change_request_body["preset_function"]["inputs"]
    model = LandCoverChangeDetectionFunctionInputs(**inputs)

    # Act
    result = model.as_ogc_process_inputs()

    # Assert
    assert result["source"] == inputs["stac_collection"]
    assert json.loads(result["aoi"]) == inputs["aoi"]
    assert result["date_start"] == inputs["date_start"]
    assert result["date_end"] == inputs["date_end"]


def test_water_quality_as_ogc_process_inputs(water_quality_request_body: dict[str, Any]) -> None:
    # Arrange
    inputs = water_quality_request_body["preset_function"]["inputs"]
    model = WaterQualityFunctionInputs(**inputs)

    # Act
    result = model.as_ogc_process_inputs()

    # Assert
    assert result["stac_collection"] == inputs["stac_collection"]
    assert json.loads(result["aoi"]) == inputs["aoi"]
    assert result["date_start"] == inputs["date_start"]
    assert result["date_end"] == inputs["date_end"]
    assert result["index"] == inputs["index"]
    assert result["calibrate"] == inputs["calibrate"]
