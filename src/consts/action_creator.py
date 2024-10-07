from __future__ import annotations

import functools
from typing import Any

from src.consts.directories import ASSETS_DIR


@functools.lru_cache
def _load_base_64_thumbnail(function_identifier: str) -> str | None:
    fp = ASSETS_DIR / f"{function_identifier}-b64.txt"
    return fp.read_text() if fp.exists() else None


RASTER_CALCULATOR_FUNCTION_SPEC = {
    "identifier": "raster-calculate",
    "name": "Raster Calculator",
    "description": "Raster calculator - calculates spectral indices.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("raster-calculate"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/raster-calculate-app.cwl",
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": ["sentinel-2-l1c", "sentinel-2-l2a"],
        },
        "date_start": {
            "type": "datetime",
            "required": False,
            "description": "The start date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "date_end": {
            "type": "datetime",
            "required": False,
            "description": "The end date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "aoi": {
            "type": "string",
            "required": False,
            "description": "The Area of Interest as GeoJSON string. Must be provided if bbox is null.",
        },
        "bbox": {
            "type": "string",
            "required": False,
            "description": "The bounding box of the area of interest. Must be provided if geometry is null.",
        },
        "index": {
            "type": "string",
            "description": "The spectral index to calculate.",
            "required": False,
            "default": "NDVI",
            "options": [
                "NDVI",
                "NDWI",
                "EVI",
                "SAVI",
            ],
        },
    },
    "outputs": {
        "collection": {
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        }
    },
}
LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC = {
    "identifier": "lulc-change",
    "name": "Land Cover Change Detection",
    "description": "Land Cover change detection.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("lulc-change"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/lulc-change-app.cwl",
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "global-land-cover",
            "description": "The STAC collection to use.",
            "options": ["global-land-cover", "corine-land-cover"],
        },
        "date_start": {
            "type": "datetime",
            "required": False,
            "description": "The start date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "date_end": {
            "type": "datetime",
            "required": False,
            "description": "The end date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "aoi": {
            "type": "string",
            "required": False,
            "description": "The Area of Interest as GeoJSON string. Must be provided if bbox is null.",
        },
        "bbox": {
            "type": "string",
            "required": False,
            "description": "The bounding box of the area of interest. Must be provided if geometry is null.",
        },
    },
    "outputs": {
        "collection": {
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        }
    },
}
WATER_QUALITY_FUNCTION_SPEC = {
    "identifier": "water-quality",
    "name": "Water Quality",
    "description": "Water Quality with calibration using DEFRA's in-situ data.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("water-quality"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/water-quality-app.cwl",
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": ["sentinel-2-l1c", "sentinel-2-l2a"],
        },
        "date_start": {
            "type": "datetime",
            "required": False,
            "description": "The start date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "date_end": {
            "type": "datetime",
            "required": False,
            "description": "The end date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "aoi": {
            "type": "string",
            "required": False,
            "description": "The Area of Interest as GeoJSON string. Must be provided if bbox is null.",
        },
        "bbox": {
            "type": "string",
            "required": False,
            "description": "The bounding box of the area of interest. Must be provided if geometry is null.",
        },
        "calibrate": {
            "type": "boolean",
            "required": False,
            "default": False,
            "description": "A flag indicating whether or not to calibrate the index formula "
            "using in-situ data from DEFRA.",
        },
        "index": {
            "type": "string",
            "description": "The spectral index to calculate.",
            "required": False,
            "default": "all",
            "options": [
                "all",
                "NDWI",
                "CDOM",
                "DOC",
                "CYA",
            ],
        },
    },
    "outputs": {
        "collection": {
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        }
    },
}

PRESET_FUNCTION_CWL_FILE_LOCATION = {
    "raster-calculator": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/raster-calculate-app.cwl",
}

FUNCTIONS = [
    RASTER_CALCULATOR_FUNCTION_SPEC,
    LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC,
    WATER_QUALITY_FUNCTION_SPEC,
]
FUNCTIONS_REGISTRY: dict[str, dict[str, Any]] = {f["identifier"]: f for f in FUNCTIONS}  # type: ignore[misc]
