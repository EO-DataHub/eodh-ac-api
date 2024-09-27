from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import pyproj
from geojson_pydantic.geometries import Polygon, parse_geometry_obj
from shapely.geometry import shape

from src.consts.action_creator import FUNCTIONS_REGISTRY

if TYPE_CHECKING:
    import shapely.geometry

EXPECTED_BBOX_ELEMENT_COUNT = 4
MAX_AREA_SQ_KM = 1000


def calculate_geodesic_area(polygon: shapely.Polygon) -> float:
    # Define the WGS 84 ellipsoid
    geod = pyproj.Geod(ellps="WGS84")

    # Get the coordinates of the polygon
    lon, lat = polygon.exterior.coords.xy

    # Calculate the geodesic area using pyproj's Geod function
    area, _ = geod.polygon_area_perimeter(lon, lat)

    # Return the area in square meters (area will be negative, so we take the absolute value)
    return float(abs(area))


def ensure_area_smaller_than(geom: dict[str, Any], area_size_limit: float = MAX_AREA_SQ_KM) -> None:
    # Parse the GeoJSON geometry (assume it's EPSG:4326)
    polygon: shapely.geometry.Polygon = shape(geom)

    # Calculate the area in square kilometers
    area_sq_km = calculate_geodesic_area(polygon) / 1e6  # Convert from square meters to square kilometers

    # Raise an error if the area exceeds MAX_AREA_SQ_KM square kilometers
    if area_sq_km > area_size_limit:
        msg = f"Area exceeds {area_size_limit} square kilometers: {area_size_limit:.2f} sq km"
        raise ValueError(msg)


def datetime_or_current_time(dt: datetime | None) -> datetime:
    return dt if dt is not None else datetime.now(timezone.utc)


def aoi_from_geojson_if_necessary(v: dict[str, Any]) -> dict[str, Any]:
    if v.get("aoi") is not None and v.get("bbox") is None and isinstance(v.get("aoi"), str):
        v["aoi"] = parse_geometry_obj(json.loads(v["aoi"]))
    return v


def aoi_from_bbox_if_necessary(v: dict[str, Any]) -> dict[str, Any]:
    if v.get("aoi") is None and v.get("bbox") is not None:
        if len(v["bbox"]) != EXPECTED_BBOX_ELEMENT_COUNT:
            msg = "BBOX object must be an array of 4 values: [xmin, ymin, xmax, ymax]"
            raise ValueError(msg)
        v["aoi"] = Polygon.from_bounds(*v["bbox"])
    return v


def validate_stac_collection(specified_collection: str, function_name: str) -> None:
    function_spec = FUNCTIONS_REGISTRY[function_name]
    if specified_collection not in (valid_collections := function_spec["inputs"]["collection"]["options"]):
        msg = (
            f"Collection '{specified_collection}' cannot be used with '{function_name}' function! "
            f"Valid options are: {valid_collections}"
        )
        raise ValueError(msg)


def validate_aoi_or_bbox_provided(v: dict[str, Any]) -> None:
    if v.get("aoi") is None and v.get("bbox") is None:
        msg = "At least one of AOI or BBOX must be provided"
        raise ValueError(msg)


def raise_if_both_aoi_and_bbox_provided(v: dict[str, Any]) -> None:
    if v.get("aoi") is not None and v.get("bbox") is not None:
        msg = "AOI and BBOX are mutually exclusive, provide only one of them."
        raise ValueError(msg)
