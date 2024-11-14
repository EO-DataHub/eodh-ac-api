from __future__ import annotations

from typing import Any

NDVI_FUNCTION_SPEC = {
    "identifier": "ndvi",
    "name": "Normalized Difference Vegetation Index (NDVI)",
    "description": "Computes NDVI spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
            ],
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
            "description": "STAC collection with results.",
        },
    },
}
EVI_FUNCTION_SPEC = {
    "identifier": "evi",
    "name": "Enhanced Vegetation Index (EVI)",
    "description": "Computes EVI spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
            ],
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
            "description": "STAC collection with results.",
        },
    },
}
SAVI_FUNCTION_SPEC = {
    "identifier": "savi",
    "name": "Soil Adjusted Vegetation Index (EVI)",
    "description": "Computes SAVI spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
            ],
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
            "description": "STAC collection with results.",
        },
    },
}
CLIP_FUNCTION_SPEC = {
    "identifier": "clip",
    "name": "Clip",
    "description": "Clip (crop) items generated by previous function using provided Area of Interest.",
    "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/clip-app.cwl",
    "compatible_input_datasets": ["sentinel-2-l2a", "esacci-globallc", "clms-corinelc", "clms-water-bodies"],
    "visible": True,
    "standalone": False,
    "inputs": {
        "aoi": {
            "type": "polygon",
            "required": True,
            "description": "The Area of Interest as GeoJSON (polygon).",
        },
    },
    "outputs": {
        "collection": {
            "type": "stac_collection",
            "description": "STAC collection with results.",
        },
    },
}
LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC = {
    "identifier": "land-cover-change-detection",
    "name": "Land Cover Change Detection",
    "description": "Computes Land Cover class percentages and occupied area",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["esacci-globallc", "clms-corinelc", "clms-water-bodies"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "ESA CCI Global Land Cover",
                    "value": "esacci-globallc",
                },
                {
                    "label": "CORINE Land Cover",
                    "value": "clms-corinelc",
                },
                {
                    "label": "Water Bodies",
                    "value": "clms-water-bodies",
                },
            ],
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
            "description": "STAC collection with results.",
        },
    },
}

FUNCTIONS = [
    NDVI_FUNCTION_SPEC,
    EVI_FUNCTION_SPEC,
    SAVI_FUNCTION_SPEC,
    CLIP_FUNCTION_SPEC,
    LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC,
]
FUNCTIONS_REGISTRY: dict[str, dict[str, Any]] = {f["identifier"]: f for f in FUNCTIONS}  # type: ignore[misc]
FUNCTION_IDENTIFIER_TO_WORKFLOW_MAPPING = {
    "evi": "raster-calculate",
    "ndvi": "raster-calculate",
    "ndwi": "raster-calculate",
    "savi": "raster-calculate",
    "land-cover-change-detection": "land-cover-change",
}
WORKFLOW_REGISTRY = {
    "land-cover-change": {
        "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/lulc-change-app.cwl",
    },
    "raster-calculate": {
        "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/raster-calculate-app.cwl",
    },
}
WORKFLOW_ID_OVERRIDE_LOOKUP = {"lulc-change": "land-cover-change", "land-cover-change": "land-cover-change"}
