from __future__ import annotations

from pydantic import BaseModel, Field

from src.api.v1_1.action_creator.schemas.workflows import WorkflowSpec  # noqa: TCH001

LAND_COVER_CHANGE_DETECTION_PRESET = {
    "inputs": {
        "area": {
            "type": "Polygon",
            "coordinates": [[[-180, 90], [180, 90], [180, -90], [-180, -90], [-180, 90]]],
        },
        "dataset": "esa-cci-glc",
        "date_start": "1994-01-01",
        "date_end": "2015-12-31",
    },
    "functions": {
        "query": {
            "identifier": "esa-glc-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["workflow", "inputs", "aoi"]},
                "stac_collection": {"$type": "ref", "value": ["workflow", "inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["workflow", "inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["workflow", "inputs", "date_end"]},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "clip": {
            "identifier": "clip",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["workflow", "steps", "query", "outputs", "results"],
                },
                "aoi": {"$type": "ref", "value": ["workflow", "inputs", "aoi"]},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "summarize_class_stats": {
            "identifier": "summarize-class-statistics",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["workflow", "steps", "clip", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
    },
}


class PresetList(BaseModel):
    presets: list[WorkflowSpec] = Field(default_factory=list)
    total: int
