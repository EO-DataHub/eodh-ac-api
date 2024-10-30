from __future__ import annotations

from src.api.v1_2.action_creator.schemas.presets import LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC
from src.api.v1_2.action_creator.schemas.workflows import WorkflowSpec


def test_lulc_change_preset_parsing() -> None:
    # Arrange
    expected = {
        "inputs": {
            "area": {
                "type": "Polygon",
                "coordinates": [[[-180.0, 90.0], [180.0, 90.0], [180.0, -90.0], [-180.0, -90.0], [-180.0, 90.0]]],
            },
            "dataset": "esa-lccci-glcm",
            "date_start": "1994-01-01T00:00:00",
            "date_end": "2015-12-31T00:00:00",
        },
        "outputs": {"results": {"name": "results", "type": "directory"}},
        "functions": {
            "query": {
                "identifier": "esa-glc-ds-query",
                "inputs": {
                    "area": {
                        "type": "Polygon",
                        "coordinates": [
                            [[-180.0, 90.0], [180.0, 90.0], [180.0, -90.0], [-180.0, -90.0], [-180.0, 90.0]]
                        ],
                    },
                    "stac_collection": "esa-lccci-glcm",
                    "date_start": "1994-01-01T00:00:00",
                    "date_end": "2015-12-31T00:00:00",
                    "limit": 10,
                },
                "outputs": {"results": {"name": "results", "type": "directory"}},
            },
            "clip": {
                "identifier": "clip",
                "inputs": {
                    "data_dir": {"name": "results", "type": "directory"},
                    "aoi": {
                        "type": "Polygon",
                        "coordinates": [
                            [[-180.0, 90.0], [180.0, 90.0], [180.0, -90.0], [-180.0, -90.0], [-180.0, 90.0]]
                        ],
                    },
                },
                "outputs": {"results": {"name": "results", "type": "directory"}},
            },
            "summarize_class_stats": {
                "identifier": "summarize-class-statistics",
                "inputs": {
                    "data_dir": {"name": "results", "type": "directory"},
                },
                "outputs": {"results": {"name": "results", "type": "directory"}},
            },
            "reproject": {
                "identifier": "reproject",
                "inputs": {
                    "data_dir": {"name": "results", "type": "directory"},
                    "epsg": "EPSG:3857",
                },
                "outputs": {"results": {"name": "results", "type": "directory"}},
            },
        },
    }

    # Act
    result = WorkflowSpec(**LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC).model_dump(
        mode="json",
        exclude_none=True,
    )

    # Assert
    assert result == expected
