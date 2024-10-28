from __future__ import annotations

import functools

from pydantic import BaseModel, Field

from src.api.v1_1.action_creator.schemas.workflow_steps import (
    DirectoryOutputs,
    DirectoryStepOutputSpec,
    InputOutputValue,
)
from src.api.v1_1.action_creator.schemas.workflows import MainWorkflowInputs
from src.consts.directories import ASSETS_DIR
from src.consts.geometries import HEATHROW_AOI, UK_AOI


@functools.lru_cache
def _load_base_64_thumbnail(function_identifier: str) -> str | None:
    fp = ASSETS_DIR / f"{function_identifier}-b64.txt"
    return fp.read_text() if fp.exists() else None


LULC_THUMBNAIL = _load_base_64_thumbnail("lulc-change")
WATER_QUALITY_THUMBNAIL = _load_base_64_thumbnail("water-quality")

LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC = {
    "inputs": {
        "area": HEATHROW_AOI,
        "dataset": "esa-lccci-glcm",
        "date_start": "1994-01-01",
        "date_end": "2015-12-31",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "esa-glc-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "clip": {
            "identifier": "clip",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
                "aoi": {"$type": "ref", "value": ["inputs", "area"]},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "summarize_class_stats": {
            "identifier": "summarize-class-statistics",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "clip", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "clip", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {
                "results": {
                    "$type": "ref",
                    "value": ["outputs", "results"],
                },
            },
        },
    },
}
LULC_CHANGE_PRESET = {
    "identifier": "lulc-change",
    "name": "Land Cover Change Detection",
    "description": "Analyses time-series satellite imagery to detect changes in land cover, identifying shifts in "
    "urban areas, forests, water bodies, and agriculture over specified periods.",
    "thumbnail_b64": _load_base_64_thumbnail("lulc-change"),
    "workflow": LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
}
WATER_QUALITY_WORKFLOW_SPEC = {
    "inputs": {
        "area": HEATHROW_AOI,
        "dataset": "sentinel-2-l2a",
        "date_start": "2024-03-01",
        "date_end": "2024-10-10",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "s2-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "clip": {
            "identifier": "clip",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
                "aoi": {"$type": "ref", "value": ["inputs", "area"]},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "cya": {
            "identifier": "cya",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "clip", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "calibrate": {
            "identifier": "defra-calibrate",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "cya", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "calibrate", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {
                "results": {
                    "$type": "ref",
                    "value": ["outputs", "results"],
                },
            },
        },
    },
}
WATER_QUALITY_PRESET = {
    "identifier": "water-quality",
    "name": "Water Quality",
    "description": "Evaluates water quality by analysing spectral data from satellite imagery, calibrated with DEFRA's "
    "in-situ measurements, to assess parameters like chlorophyll concentration and turbidity.",
    "thumbnail_b64": _load_base_64_thumbnail("water-quality"),
    "workflow": WATER_QUALITY_WORKFLOW_SPEC,
}

PRESETS = [LULC_CHANGE_PRESET, WATER_QUALITY_PRESET]
PRESET_LOOKUP = {p["identifier"]: p for p in PRESETS}

SIMPLEST_NDVI_WORKFLOW_SPEC = {
    "inputs": {
        "area": HEATHROW_AOI,
        "dataset": "sentinel-2-l2a",
        "date_start": "2024-03-01",
        "date_end": "2024-10-10",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "s2-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "ndvi": {
            "identifier": "ndvi",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
    },
}
NDVI_WORKFLOW_SPEC = {
    "inputs": {
        "area": HEATHROW_AOI,
        "dataset": "sentinel-2-l2a",
        "date_start": "2024-03-01",
        "date_end": "2024-10-10",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "s2-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "clip": {
            "identifier": "clip",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
                "aoi": {"$type": "ref", "value": ["inputs", "area"]},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "ndvi": {
            "identifier": "ndvi",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "clip", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "ndvi", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
ERR_AOI_TOO_BIG_NDVI_WORKFLOW_SPEC = {
    "inputs": {
        "area": UK_AOI,
        "dataset": "sentinel-2-l2a",
        "date_start": "2024-03-01",
        "date_end": "2024-10-10",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "s2-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "ndvi": {
            "identifier": "ndvi",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
ERR_INVALID_DATE_RANGE_NDVI_WORKFLOW_SPEC = {
    "inputs": {
        "area": HEATHROW_AOI,
        "dataset": "sentinel-2-l2a",
        "date_start": "2024-03-01",
        "date_end": "2023-10-10",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "s2-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "ndvi": {
            "identifier": "ndvi",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
ERR_INVALID_DATASET_NDVI_WORKFLOW_SPEC = {
    "inputs": {
        "area": HEATHROW_AOI,
        "dataset": "sentinel-1-grd",
        "date_start": "2024-03-01",
        "date_end": "2024-10-10",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "s2-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "ndvi": {
            "identifier": "ndvi",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
ERR_INVALID_REF_PATH_WORKFLOW_SPEC = {
    "inputs": {
        "area": HEATHROW_AOI,
        "dataset": "sentinel-2-l2a",
        "date_start": "2024-03-01",
        "date_end": "2024-10-10",
    },
    "outputs": {"results": {"name": "results", "type": "directory"}},
    "functions": {
        "query": {
            "identifier": "s2-ds-query",
            "inputs": {
                "area": {"$type": "ref", "value": ["inputs", "area"]},
                "stac_collection": {"$type": "ref", "value": ["inputs", "dataset"]},
                "date_start": {"$type": "ref", "value": ["inputs", "date_start"]},
                "date_end": {"$type": "ref", "value": ["inputs", "date_end"]},
                "limit": {"$type": "atom", "value": 10},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "ndvi": {
            "identifier": "ndvi",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "clip", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}


class WorkflowPresetStep(BaseModel):
    identifier: str
    inputs: dict[str, InputOutputValue]
    outputs: dict[str, DirectoryStepOutputSpec | InputOutputValue]


class WorkflowPresetSpec(BaseModel):
    inputs: MainWorkflowInputs
    outputs: DirectoryOutputs
    functions: dict[str, WorkflowPresetStep]


class WorkflowPreset(BaseModel):
    identifier: str
    name: str
    description: str
    thumbnail_b64: str
    workflow: WorkflowPresetSpec


class PresetList(BaseModel):
    presets: list[WorkflowPreset] = Field(default_factory=list)
    total: int
