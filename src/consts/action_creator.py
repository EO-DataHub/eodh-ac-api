from __future__ import annotations

FUNCTIONS = [
    {
        "name": "raster_calculator",
        "parameters": {
            "collection": {
                "type": "string",
                "required": False,
                "default": "sentinel-2-l2a",
                "description": "The STAC collection to use.",
                "options": ["sentinel-2-l1c", "sentinel-2-l2a"],
            },
            "start_datetime": {
                "type": "datetime",
                "required": False,
                "description": "The start date and time to use for item filtering. Must be RFC3339 compliant.",
            },
            "end_datetime": {
                "type": "datetime",
                "required": False,
                "description": "The end date and time to use for item filtering. Must be RFC3339 compliant.",
            },
            "geometry": {
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
    }
]
