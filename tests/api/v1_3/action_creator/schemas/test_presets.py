from __future__ import annotations

from src.api.v1_3.action_creator.schemas.presets import LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC
from src.api.v1_3.action_creator.schemas.workflows import WorkflowSpec
from src.consts.geometries import HEATHROW_AOI


def test_lulc_change_preset_parsing() -> None:
    # Arrange
    expected = {
        "identifier": "lcc",
        "inputs": {
            "area": HEATHROW_AOI,
            "dataset": "esa-lccci-glcm",
            "date_start": "1994-01-01T00:00:00",
            "date_end": "2015-12-31T00:00:00",
        },
        "outputs": {"results": {"name": "results", "type": "directory"}},
        "functions": {
            "query": {
                "identifier": "esa-glc-ds-query",
                "inputs": {
                    "area": HEATHROW_AOI,
                    "stac_collection": "esa-lccci-glcm",
                    "date_start": "1994-01-01T00:00:00",
                    "date_end": "2015-12-31T00:00:00",
                    "limit": 10,
                    "clip": True,
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
            "thumbnail": {
                "identifier": "thumbnail",
                "inputs": {
                    "data_dir": {
                        "name": "results",
                        "type": "directory",
                    },
                },
                "outputs": {
                    "results": {
                        "name": "results",
                        "type": "directory",
                    },
                },
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
