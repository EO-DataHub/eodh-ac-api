from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pyproj
from geojson_pydantic.geometries import parse_geometry_obj
from pydantic_core import PydanticCustomError
from shapely.geometry import shape

from src.api.v1_1.action_creator.functions import FUNCTIONS_REGISTRY as NEW_FUNCTIONS_REGISTRY
from src.consts.action_creator import FUNCTIONS_REGISTRY

if TYPE_CHECKING:
    from datetime import datetime

    import shapely.geometry

EXPECTED_BBOX_ELEMENT_COUNT = 4
MAX_AREA_SQ_KM = 1000
SQ_MILES_DIVISOR = 2.59


class AreaOfInterestTooBigError:
    @classmethod
    def make(cls, aoi: Any, max_size: float) -> PydanticCustomError:
        max_size_imperial = max_size / SQ_MILES_DIVISOR
        return PydanticCustomError(
            "area_of_interest_too_big_error",
            f"Area exceeds {max_size_imperial:,.2f} {{units_imperial}}.",
            {
                "aoi": aoi,
                "max_size_metric": max_size,
                "max_size_imperial": max_size / SQ_MILES_DIVISOR,
                "units_metric": "square kilometers",
                "units_imperial": "square miles",
            },
        )


class CollectionNotSupportedError:
    @classmethod
    def make(cls, collection: str, valid_collections: list[str], function_identifier: str) -> PydanticCustomError:
        return PydanticCustomError(
            "collection_not_supported_error",
            "Collection '{stac_collection}' cannot be used with '{function_identifier}' function! Valid options are: {valid_options}.",  # noqa: E501
            {
                "stac_collection": collection,
                "function_identifier": function_identifier,
                "valid_options": valid_collections,
            },
        )


class MissingAreaOfInterestError:
    @classmethod
    def make(cls) -> PydanticCustomError:
        return PydanticCustomError(
            "missing_area_of_interest_error",
            "Area of Interest is missing.",
            {"aoi": None},
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

    # Raise an error if the area exceeds area_size_limit square kilometers
    if area_sq_km > area_size_limit:
        raise AreaOfInterestTooBigError.make(aoi=geom, max_size=area_size_limit)


def aoi_from_geojson_if_necessary(v: dict[str, Any]) -> dict[str, Any]:
    if v.get("aoi") is not None and v.get("bbox") is None and isinstance(v.get("aoi"), str):
        v["aoi"] = parse_geometry_obj(json.loads(v["aoi"])).model_dump(mode="json")
    return v


def aoi_must_be_present(v: dict[str, Any] | None = None) -> dict[str, Any]:
    if v is None:
        raise MissingAreaOfInterestError.make()
    return v


def validate_stac_collection(specified_collection: str, function_identifier: str) -> None:
    function_spec = FUNCTIONS_REGISTRY[function_identifier]
    if specified_collection not in (valid_collections := function_spec["inputs"]["stac_collection"]["options"]):
        raise CollectionNotSupportedError.make(
            collection=specified_collection,
            valid_collections=valid_collections,
            function_identifier=function_identifier,
        )


def validate_stac_collection_v1_1(specified_collection: str, function_identifier: str) -> None:
    function_spec = NEW_FUNCTIONS_REGISTRY[function_identifier]
    if specified_collection not in (valid_collections := function_spec["compatible_input_datasets"]):
        raise CollectionNotSupportedError.make(
            collection=specified_collection,
            valid_collections=valid_collections,
            function_identifier=function_identifier,
        )


def validate_date_range(date_start: datetime | None = None, date_end: datetime | None = None) -> None:
    if date_start is None or date_end is None:
        return

    if date_start > date_end:
        raise InvalidDateRangeError.make(date_start, date_end)
