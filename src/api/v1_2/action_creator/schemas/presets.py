from __future__ import annotations

import functools
from copy import deepcopy
from typing import Any

from pydantic import BaseModel, Field

from src.api.v1_2.action_creator.schemas.workflow_tasks import (
    DirectoryOutputs,
    DirectoryTaskOutputSpec,
    InputOutputValue,
)
from src.api.v1_2.action_creator.schemas.workflows import MainWorkflowInputs
from src.consts.directories import ASSETS_DIR
from src.consts.geometries import HEATHROW_AOI, KIELDER_WATER_AOI, UK_AOI


@functools.lru_cache
def _load_base_64_thumbnail(function_identifier: str) -> str | None:
    fp = ASSETS_DIR / f"{function_identifier}-b64.txt"
    return fp.read_text() if fp.exists() else None


LULC_THUMBNAIL = _load_base_64_thumbnail("lulc-change")
WATER_QUALITY_THUMBNAIL = _load_base_64_thumbnail("water-quality")

LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC: dict[str, Any] = {
    "identifier": "lcc",
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
                "clip": {"$type": "atom", "value": True},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "summarize_class_stats": {
            "identifier": "summarize-class-statistics",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "summarize_class_stats", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "thumbnail": {
            "identifier": "thumbnail",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "reproject", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
LULC_CHANGE_PRESET: dict[str, Any] = {
    "identifier": "land-cover-change",
    "name": "Land Cover Change Detection",
    "description": "Analyses time-series satellite imagery to detect changes in land cover, identifying shifts in "
    "urban areas, forests, water bodies, and agriculture over specified periods.",
    "disabled": False,
    "thumbnail_b64": _load_base_64_thumbnail("lulc-change"),
    "workflow": LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
}
ADVANCED_WATER_QUALITY_WORKFLOW_SPEC: dict[str, Any] = {
    "identifier": "adv-wq",
    "inputs": {
        "area": KIELDER_WATER_AOI,
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
                "clip": {"$type": "atom", "value": True},
                "limit": {"$type": "atom", "value": 10},
                "cloud_cover_min": {"$type": "atom", "value": 0},
                "cloud_cover_max": {"$type": "atom", "value": 100},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "ndwi": {
            "identifier": "ndwi",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject_ndwi": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "ndwi", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "cya": {
            "identifier": "cya_cells",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject_cya": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "cya", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "doc": {
            "identifier": "doc",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject_doc": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "doc", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "cdom": {
            "identifier": "cdom",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject_cdom": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "cdom", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "stac_join_1": {
            "identifier": "stac-join",
            "inputs": {
                "stac_catalog_dir_1": {
                    "$type": "ref",
                    "value": ["functions", "reproject_cya", "outputs", "results"],
                },
                "stac_catalog_dir_2": {
                    "$type": "ref",
                    "value": ["functions", "reproject_doc", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "stac_join_2": {
            "identifier": "stac-join",
            "inputs": {
                "stac_catalog_dir_1": {
                    "$type": "ref",
                    "value": ["functions", "stac_join_1", "outputs", "results"],
                },
                "stac_catalog_dir_2": {
                    "$type": "ref",
                    "value": ["functions", "reproject_cdom", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "stac_join_3": {
            "identifier": "stac-join",
            "inputs": {
                "stac_catalog_dir_1": {
                    "$type": "ref",
                    "value": ["functions", "stac_join_2", "outputs", "results"],
                },
                "stac_catalog_dir_2": {
                    "$type": "ref",
                    "value": ["functions", "reproject_ndwi", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "thumbnail": {
            "identifier": "thumbnail",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "stac_join_3", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
WATER_QUALITY_ADVANCED_PRESET: dict[str, Any] = {
    "identifier": "water-quality",
    "name": "Water Quality",
    "description": "Evaluates water quality by analysing spectral data from satellite imagery, "
    "to assess parameters like chlorophyll concentration and turbidity.",
    "thumbnail_b64": _load_base_64_thumbnail("water-quality"),
    "disabled": True,
    "workflow": ADVANCED_WATER_QUALITY_WORKFLOW_SPEC,
}
WATER_QUALITY_WORKFLOW_SPEC: dict[str, Any] = {
    "identifier": "water-quality-wf",
    "inputs": {
        "area": KIELDER_WATER_AOI,
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
                "clip": {"$type": "atom", "value": True},
                "limit": {"$type": "atom", "value": 10},
                "cloud_cover_min": {"$type": "atom", "value": 0},
                "cloud_cover_max": {"$type": "atom", "value": 100},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "water-quality": {
            "identifier": "water-quality",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "query", "outputs", "results"],
                },
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "reproject": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "water-quality", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "thumbnail": {
            "identifier": "thumbnail",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "reproject", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
WATER_QUALITY_PRESET: dict[str, Any] = {
    "identifier": "water-quality",
    "name": "Water Quality",
    "description": "Evaluates water quality by analysing spectral data from satellite imagery, "
    "to assess parameters like chlorophyll concentration and turbidity.",
    "thumbnail_b64": _load_base_64_thumbnail("water-quality"),
    "disabled": True,
    "workflow": WATER_QUALITY_WORKFLOW_SPEC,
}

PRESETS = [LULC_CHANGE_PRESET, WATER_QUALITY_PRESET]
PRESET_LOOKUP = {p["identifier"]: p for p in PRESETS}

SIMPLEST_NDVI_WORKFLOW_SPEC: dict[str, Any] = {
    "identifier": "simplest-ndvi",
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
                "clip": {"$type": "atom", "value": True},
                "limit": {"$type": "atom", "value": 10},
                "cloud_cover_min": {"$type": "atom", "value": 0},
                "cloud_cover_max": {"$type": "atom", "value": 100},
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
        "thumbnail": {
            "identifier": "thumbnail",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "ndvi", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}
NDVI_WORKFLOW_SPEC: dict[str, Any] = {
    "identifier": "ndvi-clip-repr",
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
                "clip": {"$type": "atom", "value": True},
                "limit": {"$type": "atom", "value": 10},
                "cloud_cover_min": {"$type": "atom", "value": 0},
                "cloud_cover_max": {"$type": "atom", "value": 100},
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
        "reproject": {
            "identifier": "reproject",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "ndvi", "outputs", "results"],
                },
                "epsg": {"$type": "atom", "value": "EPSG:3857"},
            },
            "outputs": {"results": {"name": "results", "type": "directory"}},
        },
        "thumbnail": {
            "identifier": "thumbnail",
            "inputs": {
                "data_dir": {
                    "$type": "ref",
                    "value": ["functions", "reproject", "outputs", "results"],
                },
            },
            "outputs": {
                "results": {"$type": "ref", "value": ["outputs", "results"]},
            },
        },
    },
}


EXAMPLE_WORKFLOWS: dict[str, Any] = {
    "land-cover": LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
    "water-quality": WATER_QUALITY_WORKFLOW_SPEC,
    "advanced-water-quality": ADVANCED_WATER_QUALITY_WORKFLOW_SPEC,
    "simplest-ndvi": SIMPLEST_NDVI_WORKFLOW_SPEC,
    "ndvi-clip-reproject": NDVI_WORKFLOW_SPEC,
}


def area_too_big_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["inputs"]["area"] = UK_AOI
    return wf


def collection_not_supported_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["functions"].pop("reproject")
    wf["functions"]["summarize"] = {
        "identifier": "summarize-class-statistics",
        "inputs": {
            "data_dir": {
                "$type": "ref",
                "value": ["functions", "ndvi", "outputs", "results"],
            },
        },
        "outputs": {
            "results": {"$type": "ref", "value": ["outputs", "results"]},
        },
    }
    return wf


def invalid_date_range_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["inputs"]["date_start"] = "2003-01-01"
    wf["inputs"]["date_end"] = "2000-01-01"
    return wf


def too_many_tasks_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    for i in range(50):
        wf["functions"][f"ndvi-{i}"] = wf["functions"]["ndvi"]
    return wf


def tasks_have_no_outputs_mapping_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["functions"]["ndvi-2"] = {
        "identifier": "ndvi",
        "inputs": {
            "data_dir": {
                "$type": "ref",
                "value": ["functions", "query", "outputs", "results"],
            },
        },
        "outputs": {"results": {"name": "results", "type": "directory"}},
    }
    return wf


def invalid_task_order_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["functions"]["savi"] = deepcopy(wf["functions"]["ndvi"])
    wf["functions"]["savi"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "ndvi", "outputs", "results"],
    }
    wf["functions"]["savi"]["identifier"] = "savi"
    wf["functions"]["reproject"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "savi", "outputs", "results"],
    }
    return wf


def wf_output_not_mapped_to_task_result_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["outputs"]["test_output"] = {"name": "test_output", "type": "directory"}
    return wf


def invalid_path_reference_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["functions"]["ndvi"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "invalid", "function", "ref"],
    }
    return wf


def self_loop_detected_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["functions"]["reproject"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "reproject", "outputs", "results"],
    }
    return wf


def cycle_detected_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["functions"]["ndvi"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "reproject", "outputs", "results"],
    }
    return wf


def disjoined_subgraph_exist_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["functions"]["ndvi-2"] = {
        "identifier": "ndvi",
        "inputs": {
            "data_dir": {
                "$type": "atom",
                "value": {"name": "data_dir", "type": "directory"},
            },
        },
        "outputs": {
            "results": {"$type": "atom", "value": {"name": "results", "type": "directory"}},
        },
    }
    return wf


def wf_id_collision_preset() -> dict[str, Any]:
    wf = deepcopy(NDVI_WORKFLOW_SPEC)
    wf["identifier"] = "ndvi"
    return wf


AREA_TOO_BIG_PRESET = area_too_big_preset()
COLLECTION_NOT_SUPPORTED_PRESET = collection_not_supported_preset()
INVALID_DATE_RANGE_PRESET = invalid_date_range_preset()
TOO_MANY_TASKS_PRESET = too_many_tasks_preset()
TASKS_HAVE_NO_OUTPUTS_MAPPING_PRESET = tasks_have_no_outputs_mapping_preset()
INVALID_TASK_ORDER_PRESET = invalid_task_order_preset()
WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET = wf_output_not_mapped_to_task_result_preset()
INVALID_PATH_REFERENCE_PRESET = invalid_path_reference_preset()
SELF_LOOP_DETECTED_PRESET = self_loop_detected_preset()
CYCLE_DETECTED_PRESET = cycle_detected_preset()
DISJOINED_SUBGRAPH_EXIST_PRESET = disjoined_subgraph_exist_preset()
WF_ID_COLLISION_PRESET = wf_id_collision_preset()

ERROR_WF_PRESETS = {
    "err-area-too-big": {
        "summary": "Error - Area too big",
        "value": AREA_TOO_BIG_PRESET,
    },
    "err-invalid-date-range": {
        "summary": "Error - Invalid date range",
        "value": INVALID_DATE_RANGE_PRESET,
    },
    "err-invalid-dataset": {
        "summary": "Error - Dataset not supported for this function",
        "value": COLLECTION_NOT_SUPPORTED_PRESET,
    },
    "err-invalid-reference": {
        "summary": "Error - Invalid input reference path",
        "value": INVALID_PATH_REFERENCE_PRESET,
    },
    "err-invalid-task-order": {
        "summary": "Error - Invalid task order",
        "value": INVALID_TASK_ORDER_PRESET,
    },
    "err-too-many-tasks": {
        "summary": "Error - Too many tasks",
        "value": TOO_MANY_TASKS_PRESET,
    },
    "err-tasks-have-no-outputs-mapping": {
        "summary": "Error - No output mapping",
        "value": WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET,
    },
    "err-wf-output-not-mapped-to-task-result": {
        "summary": "Error - WF output not mapped to task result",
        "value": WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET,
    },
    "err-self-loop-detected": {
        "summary": "Error - Self loop detected",
        "value": SELF_LOOP_DETECTED_PRESET,
    },
    "err-cycle-detected": {
        "summary": "Error - Cycle detected",
        "value": CYCLE_DETECTED_PRESET,
    },
    "err-disjoined-subgraph-exist": {
        "summary": "Error - Disjoined subgraph exist",
        "value": DISJOINED_SUBGRAPH_EXIST_PRESET,
    },
    "err-wf-id-collision": {
        "summary": "Error - WF ID collision",
        "value": WF_ID_COLLISION_PRESET,
    },
}


class WorkflowPresetTask(BaseModel):
    identifier: str
    inputs: dict[str, InputOutputValue]
    outputs: dict[str, DirectoryTaskOutputSpec | InputOutputValue]


class WorkflowPresetSpec(BaseModel):
    inputs: MainWorkflowInputs
    outputs: DirectoryOutputs
    functions: dict[str, WorkflowPresetTask]


class WorkflowPreset(BaseModel):
    identifier: str
    name: str
    description: str
    thumbnail_b64: str
    workflow: WorkflowPresetSpec


class PresetList(BaseModel):
    presets: list[WorkflowPreset] = Field(default_factory=list)
    total: int
