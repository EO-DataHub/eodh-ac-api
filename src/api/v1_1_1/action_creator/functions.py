from __future__ import annotations

from typing import Any

NDVI_FUNCTION_SPEC = {
    "identifier": "ndvi",
    "name": "Normalized Difference Vegetation Index (NDVI)",
    "description": "Computes NDVI spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 L2A ARD",
                    "value": "sentinel-2-l2a-ard",
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
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
    "name": "Soil Adjusted Vegetation Index (SAVI)",
    "description": "Computes SAVI spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
NDWI_FUNCTION_SPEC = {
    "identifier": "ndwi",
    "name": "Normalized Difference Water Index (NDWI)",
    "description": "Computes NDWI spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
DOC_FUNCTION_SPEC = {
    "identifier": "doc",
    "name": "Dissolved Organic Compounds Index (DOC)",
    "description": "Computes DOC spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
CDOM_FUNCTION_SPEC = {
    "identifier": "cdom",
    "name": "Colored Dissolved Organic Matter Index (CDOM)",
    "description": "Computes CDOM spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
TURB_FUNCTION_SPEC = {
    "identifier": "turb",
    "name": "Turbidity Index (TURB)",
    "description": "Computes TURB spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
CYA_FUNCTION_SPEC = {
    "identifier": "cya_cells",
    "name": "Cyanobacteria Density (CYA)",
    "description": "Computes CYA spectral index.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
    "inputs": {
        "stac_collection": {
            "type": "string",
            "required": False,
            "default": "sentinel-2-l2a-ard",
            "description": "The STAC collection to use.",
            "options": [
                {
                    "label": "Sentinel 2 L2A",
                    "value": "sentinel-2-l2a",
                },
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
    "compatible_input_datasets": [
        "sentinel-2-l2a",
        "sentinel-2-l2a-ard",
        "esacci-globallc",
        "clms-corinelc",
        "clms-water-bodies",
    ],
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
WATER_QUALITY_FUNCTION_SPEC = {
    "identifier": "water-quality",
    "name": "Water Quality Analysis",
    "description": "Performs Water Quality Analysis by computing various spectral indices.",
    "visible": True,
    "standalone": True,
    "compatible_input_datasets": ["sentinel-2-l2a", "sentinel-2-l2a-ard"],
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
                {
                    "label": "Sentinel 2 ARD",
                    "value": "sentinel-2-l2a-ard",
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
    NDWI_FUNCTION_SPEC,
    DOC_FUNCTION_SPEC,
    CDOM_FUNCTION_SPEC,
    CYA_FUNCTION_SPEC,
    TURB_FUNCTION_SPEC,
    CLIP_FUNCTION_SPEC,
    LAND_COVER_CHANGE_DETECTION_FUNCTION_SPEC,
    WATER_QUALITY_FUNCTION_SPEC,
]
FUNCTIONS_REGISTRY: dict[str, dict[str, Any]] = {f["identifier"]: f for f in FUNCTIONS}  # type: ignore[misc]
FUNCTION_IDENTIFIER_TO_WORKFLOW_MAPPING = {
    "evi": "raster-calculate",
    "ndvi": "raster-calculate",
    "ndwi": "raster-calculate",
    "savi": "raster-calculate",
    "cdom": "raster-calculate",
    "doc": "raster-calculate",
    "turb": "raster-calculate",
    "cya_cells": "raster-calculate",
    "land-cover-change-detection": "land-cover-change",
    "water-quality": "water-quality",
}
WORKFLOW_REGISTRY = {
    "lulc-change": {
        "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/lulc-change-app.cwl",
    },
    "land-cover-change": {
        "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/lulc-change-app.cwl",
    },
    "raster-calculate": {
        "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/raster-calculate-app.cwl",
    },
    "water-quality": {
        "cwl_href": "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/water-quality-app.cwl",
    },
}
WORKFLOW_ID_OVERRIDE_LOOKUP = {"lulc-change": "land-cover-change", "land-cover-change": "land-cover-change"}
