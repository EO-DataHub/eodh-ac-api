from __future__ import annotations

from datetime import datetime as dt
from typing import Annotated, Any, List, Literal, Optional, Union, cast

from geojson_pydantic.geometries import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from pydantic import AfterValidator, BaseModel, Field, PositiveInt, TypeAdapter, field_validator, model_validator
from stac_pydantic.api.extensions.query import Operator
from stac_pydantic.api.extensions.sort import SortExtension
from stac_pydantic.shared import UtcDatetime

EXAMPLE_SEARCH_MODEL = {
    "sentinel-1-grd": {
        "limit": 2,
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        "filter-lang": "cql-json",
        "filter": {
            "op": "and",
            "args": [
                {
                    "op": "and",
                    "args": [
                        {"op": "=", "args": [{"property": "collection"}, "sentinel-1-grd"]},
                        {
                            "op": "or",
                            "args": [
                                {"op": "=", "args": [{"property": "properties.sat:orbit_state"}, "ascending"]},
                                {"op": "=", "args": [{"property": "properties.sat:orbit_state"}, "descending"]},
                            ],
                        },
                        {
                            "op": "or",
                            "args": [
                                {
                                    "op": "and",
                                    "args": [
                                        {"op": "=", "args": [{"property": "properties.sar:instrument_mode"}, "EW"]},
                                        {
                                            "op": "and",
                                            "args": [
                                                {
                                                    "op": "in",
                                                    "args": [{"property": "properties.sar:polarizations"}, ["HH"]],
                                                },
                                                {
                                                    "op": "in",
                                                    "args": [{"property": "properties.sar:polarizations"}, ["HV"]],
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "op": "and",
                                    "args": [
                                        {"op": "=", "args": [{"property": "properties.sar:instrument_mode"}, "IW"]},
                                        {
                                            "op": "and",
                                            "args": [
                                                {
                                                    "op": "in",
                                                    "args": [{"property": "properties.sar:polarizations"}, ["VV"]],
                                                },
                                                {
                                                    "op": "in",
                                                    "args": [{"property": "properties.sar:polarizations"}, ["VH"]],
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
                {
                    "op": "between",
                    "args": [
                        {"property": "properties.datetime"},
                        "2022-12-24T00:00:00.000Z",
                        "2025-01-24T23:59:59.999Z",
                    ],
                },
            ],
        },
        "fields": {
            "include": ["properties.sar:instrument_mode", "properties.sar:polarizations", "properties.sat:orbit_state"],
            "exclude": [],
        },
        "intersects": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-8.091622055952188, -14.106928039803392],
                    [79.47934179206167, -14.106928039803392],
                    [79.47934179206167, 54.95732114609001],
                    [-8.091622055952188, 54.95732114609001],
                    [-8.091622055952188, -14.106928039803392],
                ]
            ],
        },
    },
    "sentinel-2-l1c": {
        "limit": 2,
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        "collections": [],
        "filter-lang": "cql-json",
        "filter": {
            "op": "and",
            "args": [
                {"op": "<=", "args": [{"property": "properties.eo:cloud_cover"}, 100]},
                {
                    "op": "between",
                    "args": [
                        {"property": "properties.datetime"},
                        "2022-12-23T00:00:00.000Z",
                        "2025-01-23T23:59:59.999Z",
                    ],
                },
            ],
        },
        "fields": {"include": ["properties.eo:cloud_cover", "properties.grid:code"], "exclude": []},
        "intersects": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-8.091622055952188, -14.106928039803392],
                    [79.47934179206167, -14.106928039803392],
                    [79.47934179206167, 54.95732114609001],
                    [-8.091622055952188, 54.95732114609001],
                    [-8.091622055952188, -14.106928039803392],
                ]
            ],
        },
    },
    "sentinel-2-l2a": {
        "limit": 2,
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        "collections": [],
        "filter-lang": "cql-json",
        "filter": {
            "op": "and",
            "args": [
                {"op": "<=", "args": [{"property": "properties.eo:cloud_cover"}, 100]},
                {
                    "op": "between",
                    "args": [
                        {"property": "properties.datetime"},
                        "2022-12-23T00:00:00.000Z",
                        "2025-01-23T23:59:59.999Z",
                    ],
                },
            ],
        },
        "fields": {"include": ["properties.eo:cloud_cover", "properties.grid:code"], "exclude": []},
        "intersects": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-8.091622055952188, -14.106928039803392],
                    [79.47934179206167, -14.106928039803392],
                    [79.47934179206167, 54.95732114609001],
                    [-8.091622055952188, 54.95732114609001],
                    [-8.091622055952188, -14.106928039803392],
                ]
            ],
        },
    },
    "sentinel-2-l2a-ard": {
        "limit": 2,
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        "collections": [],
        "filter-lang": "cql-json",
        "filter": {
            "op": "and",
            "args": [
                {"op": "<=", "args": [{"property": "properties.eo:cloud_cover"}, 100]},
                {
                    "op": "between",
                    "args": [
                        {"property": "properties.datetime"},
                        "2022-12-23T00:00:00.000Z",
                        "2025-01-23T23:59:59.999Z",
                    ],
                },
            ],
        },
        "fields": {"include": ["properties.eo:cloud_cover", "properties.grid:code"], "exclude": []},
        "intersects": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-8.091622055952188, -14.106928039803392],
                    [79.47934179206167, -14.106928039803392],
                    [79.47934179206167, 54.95732114609001],
                    [-8.091622055952188, 54.95732114609001],
                    [-8.091622055952188, -14.106928039803392],
                ]
            ],
        },
    },
}


def crop(v: PositiveInt) -> PositiveInt:
    """Crop value to 10,000."""
    return min(v, 10_000)


Limit = Annotated[PositiveInt, AfterValidator(crop)]
Intersection = Union[
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    GeometryCollection,
]
SearchDatetime = TypeAdapter(Optional[UtcDatetime])


class FieldsExtension(BaseModel):
    include: set[str] = Field(None)
    exclude: set[str] = Field(None)


class StacSearch(BaseModel):
    token: str | None = None
    limit: Limit = Field(
        100,
        description="Limits the number of results that are included in each page of the response (capped to 10_000).",
    )
    max_items: int | None = Field(
        None,
        description="The maximum number of items to return from the search, even if there are more matching results.",
    )
    fields: FieldsExtension | None = Field(None)
    query: dict[str, dict[Operator, Any]] | None = None
    sortby: list[SortExtension] | None = None
    filter: dict[str, Any] | None = Field(default=None, description="A CQL filter expression for filtering items.")
    filter_lang: Literal["cql-json", "cql2-json"] | None = Field(
        alias="filter-lang",
        default="cql2-json",
        description="The CQL filter encoding that the 'filter' value uses.",
    )
    intersects: Intersection | None = None
    datetime: str | None = None

    # Private properties to store the parsed datetime values. Not part of the model schema.
    _start_date: dt | None = None
    _end_date: dt | None = None

    # Properties to return the private values
    @property
    def start_date(self) -> dt | None:
        return self._start_date

    @property
    def end_date(self) -> dt | None:
        return self._end_date

    @model_validator(mode="before")
    @classmethod
    def validate_spatial(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("intersects") and values.get("bbox") is not None:
            msg = "intersects and bbox parameters are mutually exclusive"
            raise ValueError(msg)
        return values

    @field_validator("datetime")
    @classmethod
    def validate_datetime(cls, value: str) -> str:
        # Split on "/" and replace no value or ".." with None
        values = [v if v and v != ".." else None for v in value.split("/")]

        # If there are more than 2 dates, it's invalid
        if len(values) > 2:  # noqa: PLR2004
            msg = "Invalid datetime range. Too many values. Must match format: {begin_date}/{end_date}"
            raise ValueError(msg)

        # If there is only one date, duplicate to use for both start and end dates
        if len(values) == 1:
            values = [values[0], values[0]]

        # Cast because pylance gets confused by the type adapter and annotated type
        dates = cast(
            List[Optional[dt]],
            [
                # Use the type adapter to validate the datetime strings, strict is necessary
                # due to pydantic issues #8736 and #8762
                SearchDatetime.validate_strings(v, strict=True) if v else None
                for v in values
            ],
        )

        # If there is a start and end date, check that the start date is before the end date
        if dates[0] and dates[1] and dates[0] > dates[1]:
            msg = "Invalid datetime range. Begin date after end date. " "Must match format: {begin_date}/{end_date}"
            raise ValueError(msg)

        # Store the parsed dates
        cls._start_date = dates[0]
        cls._end_date = dates[1]
        # Return the original string value
        return value

    @property
    def spatial_filter(self) -> Intersection | None:
        """Return a geojson-pydantic object representing the spatial filter for the search request.

        Check for both because the ``intersects`` parameters are mutually exclusive.

        """
        if self.intersects:
            return self.intersects
        return None


class ExtendedStacSearch(StacSearch):
    ids: list[str] | None = None
    collections: list[str] | None = None
