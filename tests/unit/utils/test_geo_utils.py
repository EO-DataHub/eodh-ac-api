from __future__ import annotations

from typing import Any

import pytest
from shapely.geometry.geo import shape

from src.utils.geo import calculate_geodesic_area, chip_aoi
from tests.unit.services.test_validation_utils import FEATURES


@pytest.mark.parametrize(
    "feature",
    FEATURES,
    ids=lambda feature: feature["properties"]["id"],
)
def test_polygon_area_expected_results(feature: dict[str, Any]) -> None:
    # Act
    result = calculate_geodesic_area(shape(feature["geometry"]))

    # Assert
    assert pytest.approx(result / 1_000_000, rel=1e-3) == feature["properties"]["area"]


@pytest.mark.parametrize(
    "feature",
    FEATURES,
    ids=lambda feature: feature["properties"]["id"],
)
def test_chipping(feature: dict[str, Any]) -> None:
    # Arrange
    expected_max_size = 1000

    # Act
    result = chip_aoi(shape(feature["geometry"]), chip_size_deg=0.2)

    # Assert
    for feat in result:
        assert feat["type"] == "Polygon"
        assert calculate_geodesic_area(shape(feat)) / 1e6 < expected_max_size
