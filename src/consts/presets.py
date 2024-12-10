from __future__ import annotations

import functools

from src.consts.aoi import HEATHROW_AOI, INDIAN_OCEAN_AOI
from src.consts.directories import ASSETS_DIR


@functools.lru_cache
def _load_base_64_thumbnail(function_identifier: str) -> str | None:
    fp = ASSETS_DIR / f"{function_identifier}-b64.txt"
    return fp.read_text() if fp.exists() else None


LAND_COVER_CHANGE_DETECTION_PRESET_SPEC = {
    "identifier": "land-cover-change-detection",
    "name": "Land Cover Change Detection",
    "description": "Analyses time-series satellite imagery to detect changes in land cover, identifying shifts in "
    "urban areas, forests, water bodies, and agriculture over specified periods.",
    "thumbnail_b64": _load_base_64_thumbnail("lulc-change"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/lulc-change-app.cwl",
    "visible": True,
    "disabled": False,
    "workflow": {
        "land-cover-change-detection": {
            "identifier": "land-cover-change-detection",
            "order": 0,
            "inputs": {
                "stac_collection": "esacci-globallc",
                "date_start": "1992-01-01T00:00:00Z",
                "date_end": "2015-12-31T23:59:59Z",
                "aoi": HEATHROW_AOI,
            },
        },
        "clip": {
            "identifier": "clip",
            "order": 1,
            "inputs": {
                "aoi": HEATHROW_AOI,
            },
        },
    },
}

WATER_QUALITY_PRESET_SPEC = {
    "identifier": "water-quality",
    "name": "Water Quality",
    "description": "Evaluates water quality by analysing spectral data from satellite imagery, calibrated with DEFRA's "
    "in-situ measurements, to assess parameters like chlorophyll concentration and turbidity.",
    "thumbnail_b64": _load_base_64_thumbnail("water-quality"),
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/water-quality-app.cwl",
    "visible": True,
    "disabled": False,
    "workflow": {
        "water-quality": {
            "identifier": "water-quality",
            "order": 0,
            "inputs": {
                "stac_collection": "sentinel-2-l2a",
                "date_start": "2024-01-01T00:00:00Z",
                "date_end": "2024-12-31T23:59:59Z",
                "aoi": INDIAN_OCEAN_AOI,
            },
        }
    },
}


NDVI_PRESET = {
    "workflow": {
        "ndvi": {
            "identifier": "ndvi",
            "order": 0,
            "inputs": {
                "stac_collection": "sentinel-2-l2a",
                "date_start": "2024-01-01T00:00:00Z",
                "date_end": "2024-12-31T23:59:59Z",
                "aoi": INDIAN_OCEAN_AOI,
            },
        }
    }
}

NDVI_CLIP_PRESET = {
    "workflow": {
        "ndvi": {
            "identifier": "ndvi",
            "order": 0,
            "inputs": {
                "stac_collection": "sentinel-2-l2a",
                "date_start": "2024-01-01T00:00:00Z",
                "date_end": "2024-12-31T23:59:59Z",
                "aoi": INDIAN_OCEAN_AOI,
            },
        },
        "clip": {
            "identifier": "clip",
            "order": 1,
            "inputs": {
                "aoi": INDIAN_OCEAN_AOI,
            },
        },
    }
}

WATER_QUALITY_PRESET = {
    "workflow": WATER_QUALITY_PRESET_SPEC["workflow"],
}

PRESETS = [LAND_COVER_CHANGE_DETECTION_PRESET_SPEC, WATER_QUALITY_PRESET_SPEC]
