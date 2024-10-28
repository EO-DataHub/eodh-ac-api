from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from geojson_pydantic import Polygon

from src.api.v1_0.action_creator.schemas import RasterCalculatorFunctionInputs, RasterCalculatorIndex
from src.consts.geometries import HEATHROW_AOI, UK_AOI


def test_raster_calculate_preset_validation_no_aoi_provided() -> None:
    data = {
        "aoi": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Area of Interest is missing."):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_aoi_too_big() -> None:
    # Arrange
    data = {
        "aoi": UK_AOI,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Area exceeds"):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_raises_for_unsupported_collection() -> None:
    data = {
        "aoi": HEATHROW_AOI,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "test",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Collection 'test' cannot be used"):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_raises_for_invalid_date_range() -> None:
    data = {
        "aoi": HEATHROW_AOI,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2023-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="End date cannot be before start date."):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_uses_ndvi_if_index_not_provided() -> None:
    data = {
        "aoi": HEATHROW_AOI,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data)

    # Assert
    assert result.index == RasterCalculatorIndex.NDVI


def test_raster_calculate_preset_validation_happy_path() -> None:
    data = {
        "aoi": HEATHROW_AOI,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data)

    # Assert
    assert result.aoi == Polygon(**HEATHROW_AOI)
    assert result.date_start == datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert result.date_end == datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert result.stac_collection == "sentinel-2-l2a"
    assert result.index == "EVI"


def test_raster_calculation_inputs() -> None:
    data = {
        "aoi": HEATHROW_AOI,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data).as_ogc_process_inputs()

    # Assert
    assert json.loads(result["aoi"]) == HEATHROW_AOI
    assert result["date_start"] == "2024-01-01T00:00:00+00:00"
    assert result["date_end"] == "2024-01-01T00:00:00+00:00"
    assert result["stac_collection"] == "sentinel-2-l2a"
    assert result["index"] == "EVI"
