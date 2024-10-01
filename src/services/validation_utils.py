from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pyproj
from geojson_pydantic.geometries import Polygon, parse_geometry_obj
from pydantic_core import PydanticCustomError
from shapely.geometry import shape

from src.consts.action_creator import FUNCTIONS_REGISTRY

if TYPE_CHECKING:
    import shapely.geometry

EXPECTED_BBOX_ELEMENT_COUNT = 4
MAX_AREA_SQ_KM = 1000


class AreaOfInterestTooBigError:
    @classmethod
    def make(cls, aoi: Any, max_size: float) -> PydanticCustomError:
        return PydanticCustomError(
            "area_of_interest_too_big_error",
            "Area exceeds {max_size} sq kilometers.",
            {"aoi": aoi, "max_size": max_size},
        )


class InvalidBoundingBoxError:
    @classmethod
    def make(cls, bbox: tuple[float, ...]) -> PydanticCustomError:
        return PydanticCustomError(
            "invalid_bounding_box_error",
            "BBOX object must be an array of 4 values: [xmin, ymin, xmax, ymax]",
            {"bbox": bbox},
        )


class CollectionNotSupportedError:
    @classmethod
    def make(cls, collection: str, valid_collections: list[str], function_identifier: str) -> PydanticCustomError:
        return PydanticCustomError(
            "collection_not_supported_error",
            "Collection '{stac_collection}' cannot be used with '{function_identifier}' function! Valid options are: {valid_options}",  # noqa: E501
            {
                "stac_collection": collection,
                "function_identifier": function_identifier,
                "valid_options": valid_collections,
            },
        )


class MissingGeometryError:
    @classmethod
    def make(cls) -> PydanticCustomError:
        return PydanticCustomError(
            "missing_geometry_error",
            "At least one of AOI or BBOX must be provided.",
            {"aoi": None, "bbox": None},
        )


class AOIBBoxMisconfigurationError:
    @classmethod
    def make(cls, aoi: Any, bbox: Any) -> PydanticCustomError:
        return PydanticCustomError(
            "aoi_bbox_misconfiguration_error",
            "AOI and BBOX are mutually exclusive, provide only one of them.",
            {"aoi": aoi, "bbox": bbox},
        )


class InvalidDateRangeError:
    @classmethod
    def make(cls, date_start: datetime, date_end: datetime) -> PydanticCustomError:
        return PydanticCustomError(
            "invalid_date_range_error",
            "End date cannot be before start date.",
            {"date_start": date_start, "date_end": date_end},
        )


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
        raise AreaOfInterestTooBigError.make(aoi=geom, max_size=area_size_limit)


def aoi_from_geojson_if_necessary(v: dict[str, Any]) -> dict[str, Any]:
    if v.get("aoi") is not None and v.get("bbox") is None and isinstance(v.get("aoi"), str):
        v["aoi"] = parse_geometry_obj(json.loads(v["aoi"])).model_dump(mode="json")
    return v


def aoi_from_bbox_if_necessary(v: dict[str, Any]) -> dict[str, Any]:
    if v.get("aoi") is None and v.get("bbox") is not None:
        if len(v["bbox"]) != EXPECTED_BBOX_ELEMENT_COUNT:
            raise InvalidBoundingBoxError.make(bbox=v["bbox"])
        v["aoi"] = Polygon.from_bounds(*v["bbox"]).model_dump(mode="json")
    return v


def validate_stac_collection(specified_collection: str, function_identifier: str) -> None:
    function_spec = FUNCTIONS_REGISTRY[function_identifier]
    if specified_collection not in (valid_collections := function_spec["inputs"]["stac_collection"]["options"]):
        raise CollectionNotSupportedError.make(
            collection=specified_collection,
            valid_collections=valid_collections,
            function_identifier=function_identifier,
        )


def validate_aoi_or_bbox_provided(v: dict[str, Any]) -> None:
    if v.get("aoi") is None and v.get("bbox") is None:
        raise MissingGeometryError.make()


def raise_if_both_aoi_and_bbox_provided(v: dict[str, Any]) -> None:
    if v.get("aoi") is not None and v.get("bbox") is not None:
        raise AOIBBoxMisconfigurationError.make(aoi=v.get("aoi"), bbox=v.get("bbox"))


def validate_date_range(v: dict[str, Any]) -> None:
    date_start = v.get("date_start")
    date_end = v.get("date_end")

    if date_start is None or date_end is None:
        return

    date_start = datetime.fromisoformat(date_start)
    date_end = datetime.fromisoformat(date_end)

    if date_start > date_end:
        raise InvalidDateRangeError.make(date_start, date_end)
