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
    "description": "Performs pixel-level calculations on raster datasets to compute indices such as NDVI, EVI, "
    "and other spectral indicators, enabling vegetation and land surface analysis.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("raster-calculate"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/raster-calculate-app.cwl",
    "inputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": ["sentinel-2-l2a"],
        },
        "date_start": {
            "name": "date_start",
            "full_name": "Start date",
            "type": "datetime",
            "required": False,
            "description": "The start date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "date_end": {
            "name": "date_end",
            "full_name": "End date",
            "type": "datetime",
            "required": False,
            "description": "The end date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "aoi": {
            "name": "aoi",
            "full_name": "Area of Interest",
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
        },
    },
    "parameters": {
        "index": {
            "name": "index",
            "full_name": "Spectral index",
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
        "limit": {
            "name": "limit",
            "full_name": "Result number limit",
            "type": "number",
            "required": False,
            "default": 1,
            "description": "The number of latest items to process.",
        },
    },
    "outputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        },
    },
}
LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC = {
    "identifier": "lulc-change",
    "name": "Land Cover Change Detection",
    "description": "Analyses time-series satellite imagery to detect changes in land cover, identifying shifts in "
    "urban areas, forests, water bodies, and agriculture over specified periods.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("lulc-change"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/lulc-change-app.cwl",
    "inputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": ["esacci-globallc", "clms-corinelc", "clms-water-bodies"],
        },
        "date_start": {
            "name": "date_start",
            "full_name": "Start date",
            "type": "datetime",
            "required": False,
            "description": "The start date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "date_end": {
            "name": "date_end",
            "full_name": "End date",
            "type": "datetime",
            "required": False,
            "description": "The end date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "aoi": {
            "name": "aoi",
            "full_name": "Area of Interest",
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
        },
    },
    "outputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        },
    },
}
WATER_QUALITY_FUNCTION_SPEC = {
    "identifier": "water-quality",
    "name": "Water Quality",
    "description": "Evaluates water quality by analysing spectral data from satellite imagery, calibrated with DEFRA's "
    "in-situ measurements, to assess parameters like chlorophyll concentration and turbidity.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("water-quality"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/water-quality-app.cwl",
    "inputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": ["sentinel-2-l2a"],
        },
        "date_start": {
            "name": "date_start",
            "full_name": "Start date",
            "type": "datetime",
            "required": False,
            "description": "The start date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "date_end": {
            "name": "date_end",
            "full_name": "End date",
            "type": "datetime",
            "required": False,
            "description": "The end date and time to use for item filtering. Must be RFC3339 compliant.",
        },
        "aoi": {
            "name": "aoi",
            "full_name": "Area of Interest",
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
        },
    },
    "parameters": {
        "calibrate": {
            "name": "calibrate",
            "full_name": "In-situ data calibration",
            "type": "boolean",
            "required": False,
            "default": False,
            "description": "A flag indicating whether or not to calibrate the index formula "
            "using in-situ data from DEFRA.",
        },
        "index": {
            "name": "index",
            "full_name": "Quality index",
            "type": "string",
            "description": "The spectral index to calculate.",
            "required": False,
            "default": "NDWI",
            "options": [
                "NDWI",
                "CDOM",
                "DOC",
                "CYA",
            ],
        },
    },
    "outputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        },
    },
}
CLIP_FUNCTION_SPEC = {
    "identifier": "clip",
    "name": "Clip",
    "description": "Clip (crop) items generated by previous function using provided Area of Interest.",
    "standalone": False,
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/clip-app.cwl",
    "inputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "stac_collection",
            "required": True,
            "description": "The STAC collection with items from previous function block.",
        },
        "aoi": {
            "name": "aoi",
            "full_name": "Area of Interest",
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon) for item cropping.",
        },
    },
    "outputs": {
        "stac_collection": {
            "name": "stac_collection",
            "full_name": "STAC collection",
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        },
    },
}

PRESETS = [
    RASTER_CALCULATOR_FUNCTION_SPEC,
    LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC,
    WATER_QUALITY_FUNCTION_SPEC,
]
FUNCTIONS = [
    CLIP_FUNCTION_SPEC,
]
PRESETS_REGISTRY: dict[str, dict[str, Any]] = {f["identifier"]: f for f in PRESETS}  # type: ignore[misc]
FUNCTIONS_REGISTRY: dict[str, dict[str, Any]] = {f["identifier"]: f for f in FUNCTIONS}  # type: ignore[misc]
