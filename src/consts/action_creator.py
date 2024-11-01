from __future__ import annotations

import functools
from typing import Any

from src.consts.directories import ASSETS_DIR


@functools.lru_cache
def _load_base_64_thumbnail(function_identifier: str) -> str | None:
    fp = ASSETS_DIR / f"{function_identifier}-b64.txt"
    return fp.read_text() if fp.exists() else None


LULC_THUMBNAIL = _load_base_64_thumbnail("lulc-change")
WATER_QUALITY_THUMBNAIL = _load_base_64_thumbnail("water-quality")
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
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": ["sentinel-2-l2a"],
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
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
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
        "limit": {
            "type": "number",
            "required": False,
            "default": 25,
            "description": "The number of latest items to process.",
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
    "description": "Analyses time-series satellite imagery to detect changes in land cover, identifying shifts in "
    "urban areas, forests, water bodies, and agriculture over specified periods.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("lulc-change"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/lulc-change-app.cwl",
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "esacci-globallc",
            "description": "The STAC collection to use.",
            "options": ["esacci-globallc", "clms-corinelc", "clms-water-bodies"],
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
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
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
    "description": "Evaluates water quality by analysing spectral data from satellite imagery, calibrated with DEFRA's "
    "in-situ measurements, to assess parameters like chlorophyll concentration and turbidity.",
    "preset": True,
    "thumbnail_b64": _load_base_64_thumbnail("water-quality"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/water-quality-app.cwl",
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": ["sentinel-2-l2a"],
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
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
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
        "collection": {
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        }
    },
}
CLIP_FUNCTION_SPEC = {
    "identifier": "clip",
    "name": "Clip",
    "description": "Clip (crop) items generated by previous function using provided Area of Interest.",
    "preset": False,
    "thumbnail_b64": _load_base_64_thumbnail("clip"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/clip-app.cwl",
    "inputs": {
        "collection": {
            "type": "stac_collection",
            "required": True,
            "description": "The STAC collection to use.",
        },
        "aoi": {
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
        },
    },
    "outputs": {
        "collection": {
            "type": "stac_collection",
            "description": "The STAC collection with results.",
        }
    },
}

FUNCTIONS = [
    RASTER_CALCULATOR_FUNCTION_SPEC,
    LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC,
    WATER_QUALITY_FUNCTION_SPEC,
    CLIP_FUNCTION_SPEC,
]
FUNCTIONS_REGISTRY: dict[str, dict[str, Any]] = {f["identifier"]: f for f in FUNCTIONS}  # type: ignore[misc]
