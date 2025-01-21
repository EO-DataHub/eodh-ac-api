from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from geojson_pydantic.geometries import parse_geometry_obj
from pydantic_core import PydanticCustomError
from shapely.geometry import shape

from src.api.v1_1.action_creator.functions import FUNCTIONS_REGISTRY as NEW_FUNCTIONS_REGISTRY_V1_1
from src.api.v1_2.action_creator.functions import FUNCTIONS_REGISTRY as NEW_FUNCTIONS_REGISTRY_v1_2  # noqa: N811
from src.consts.action_creator import FUNCTIONS_REGISTRY
from src.utils.geo import calculate_geodesic_area

if TYPE_CHECKING:
    import shapely.geometry

EXPECTED_BBOX_ELEMENT_COUNT = 4
MAX_AREA_SQ_KM = 20_000
CHIPPING_THRESHOLD_SQ_KM = 2500
SQ_MILES_DIVISOR = 2.59

STAC_COLLECTION_DATE_RANGE_LOOKUP = {
    "sentinel-1-grd": (
        datetime.fromisoformat("2014-10-10T10:28:21+00:00"),
        None,
    ),
    "sentinel-2-l1c": (
        datetime.fromisoformat("2015-06-27T10:25:31+00:00"),
        None,
    ),
    "sentinel-2-l2a": (
        datetime.fromisoformat("2015-06-27T10:25:31+00:00"),
        None,
    ),
    "sentinel-2-l2a-ard": (
        datetime.fromisoformat("2015-06-27T10:25:31+00:00"),
        None,
    ),
    "esacci-globallc": (
        datetime.fromisoformat("1992-01-01T00:00:00+00:00"),
        datetime.fromisoformat("2015-12-31T23:59:59+00:00"),
    ),
    "clms-corinelc": (
        datetime.fromisoformat("1990-01-01T00:00:00+00:00"),
        datetime.fromisoformat("2018-12-31T23:59:59+00:00"),
    ),
    "clms-water-bodies": (
        datetime.fromisoformat("2020-01-01T00:00:00+00:00"),
        None,
    ),
}


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


class StacDateRangeError:
    @classmethod
    def make(
        cls,
        collection: str,
        valid_start: datetime | None = None,
        valid_end: datetime | None = None,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> PydanticCustomError:
        return PydanticCustomError(
            "stac_date_range_error",
            "Invalid date range for selected STAC collection: {collection}. Valid range is between {valid_start} and {valid_end}.",  # noqa: E501
            {
                "valid_start": valid_start.isoformat() if valid_start else None,
                "valid_end": valid_end.isoformat() if valid_end else None,
                "date_start": date_start,
                "date_end": date_end,
                "collection": collection,
            },
        )


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
    function_spec = NEW_FUNCTIONS_REGISTRY_V1_1[function_identifier]
    if specified_collection not in (valid_collections := function_spec["compatible_input_datasets"]):
        raise CollectionNotSupportedError.make(
            collection=specified_collection,
            valid_collections=valid_collections,
            function_identifier=function_identifier,
        )


def validate_stac_collection_v1_2(specified_collection: str, function_identifier: str) -> None:
    function_spec = NEW_FUNCTIONS_REGISTRY_v1_2[function_identifier]
    if specified_collection not in (valid_collections := function_spec["compatible_input_datasets"]):
        raise CollectionNotSupportedError.make(
            collection=specified_collection,
            valid_collections=valid_collections,
            function_identifier=function_identifier,
        )


def validate_stac_date_range(
    stac_collection: str,
    date_start: datetime | None = None,
    date_end: datetime | None = None,
) -> None:
    valid_date_min, valid_date_max = STAC_COLLECTION_DATE_RANGE_LOOKUP[stac_collection]
    if date_start is not None:
        date_start = (
            date_start.replace(tzinfo=timezone.utc)
            if date_start.tzinfo is None
            else date_start.astimezone(tz=timezone.utc)
        )
    if date_end is not None:
        date_end = (
            date_end.replace(tzinfo=timezone.utc) if date_end.tzinfo is None else date_end.astimezone(tz=timezone.utc)
        )

    if date_start is not None and (
        (valid_date_min is not None and date_start < valid_date_min)
        or (valid_date_max is not None and date_start > valid_date_max)
    ):
        raise StacDateRangeError.make(
            collection=stac_collection,
            date_start=date_start,
            date_end=date_end,
            valid_start=valid_date_min,
            valid_end=valid_date_max,
        )

    if date_end is not None and (
        (valid_date_min is not None and date_end < valid_date_min)
        or (valid_date_max is not None and date_end > valid_date_max)
    ):
        raise StacDateRangeError.make(
            collection=stac_collection,
            date_start=date_start,
            date_end=date_end,
            valid_start=valid_date_min,
            valid_end=valid_date_max,
        )


def validate_date_range(date_start: datetime | None = None, date_end: datetime | None = None) -> None:
    if date_start is None or date_end is None:
        return

    if date_start > date_end:
        raise InvalidDateRangeError.make(date_start, date_end)
