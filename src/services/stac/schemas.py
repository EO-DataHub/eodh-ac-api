from __future__ import annotations

import datetime as dt  # noqa: TC003
from typing import Annotated, Any, Literal, NamedTuple, Union, cast

from geojson_pydantic import GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon
from pydantic import AfterValidator, BaseModel, Field, PositiveInt, TypeAdapter, field_validator, model_validator
from stac_pydantic.api.extensions.query import Operator  # noqa: TC002
from stac_pydantic.api.extensions.sort import SortExtension  # noqa: TC002
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
EXAMPLE_SEARCH_NEXT_PAGE = {
    "sentinel-2-l2a-ard": {
        "token": "MTcwMDIxOTYxMTAwMA==",
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
    }
}
EXAMPLE_FEATURE = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-1.952174058127168, 54.05289848105603],
                [-1.89686988356467, 54.17321996032073],
                [-1.830315805751255, 54.31865051396965],
                [-1.763325793361353, 54.46402291216936],
                [-1.695601675714164, 54.60923958596745],
                [-1.627918237742603, 54.75444826231429],
                [-1.559891762794477, 54.89960493766007],
                [-1.495382803369573, 55.036369194576146],
                [-1.282265773165896, 55.03486571697855],
                [-1.323211871875057, 54.04851470634905],
                [-1.952174058127168, 54.05289848105603],
            ]
        ],
    },
    "properties": {"datetime": "2023-11-17T11:13:31+00:00", "eo:cloud_cover": "0.303176949448"},
    "id": "neodc.sentinel_ard.data.sentinel_2.2023.11.17.S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb",  # noqa: E501
    "bbox": [-1.952174058127168, 54.04851470634905, -1.282265773165896, 55.036369194576146],
    "stac_version": "1.0.0",
    "assets": {
        "cloud": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_clouds.tif",
            "roles": ["data"],
            "location": "on_disk",
            "size": 1655645,
        },
        "cloud_probability": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_clouds_prob.tif",
            "roles": ["data"],
            "location": "on_disk",
            "size": 26592509,
        },
        "cog": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_vmsk_sharp_rad_srefdem_stdsref.tif",
            "roles": ["data"],
            "location": "on_disk",
            "eo:bands": [
                {
                    "eo:central_wavelength": 496.6,
                    "eo:common_name": "blue",
                    "description": "Blue",
                    "eo: full_width_half_max": 0.07,
                    "name": "B02",
                },
                {
                    "eo:central_wavelength": 560,
                    "eo:common_name": "green",
                    "description": "Green",
                    "eo: full_width_half_max": 0.04,
                    "name": "B03",
                },
                {
                    "eo:central_wavelength": 664.5,
                    "eo:common_name": "red",
                    "description": "Red",
                    "eo: full_width_half_max": 0.03,
                    "name": "B04",
                },
                {
                    "eo:central_wavelength": 703.9,
                    "eo:common_name": "rededge",
                    "description": "Visible and Near Infrared",
                    "eo: full_width_half_max": 0.02,
                    "name": "B05",
                },
                {
                    "eo:central_wavelength": 740.2,
                    "eo:common_name": "rededge",
                    "description": "Visible and Near Infrared",
                    "eo: full_width_half_max": 0.02,
                    "name": "B06",
                },
                {
                    "eo:central_wavelength": 782.5,
                    "eo:common_name": "rededge",
                    "description": "Visible and Near Infrared",
                    "eo: full_width_half_max": 0.02,
                    "name": "B07",
                },
                {
                    "eo:central_wavelength": 835.1,
                    "eo:common_name": "nir",
                    "description": "Visible and Near Infrared",
                    "eo: full_width_half_max": 0.11,
                    "name": "B08",
                },
                {
                    "eo:central_wavelength": 864.8,
                    "eo:common_name": "nir08",
                    "description": "Visible and Near Infrared",
                    "eo: full_width_half_max": 0.02,
                    "name": "B08a",
                },
                {
                    "eo:central_wavelength": 1613.7,
                    "eo:common_name": "swir16",
                    "description": "Short Wave Infrared",
                    "eo: full_width_half_max": 0.09,
                    "name": "B11",
                },
                {
                    "eo:central_wavelength": 2202.4,
                    "eo:common_name": "swir22",
                    "description": "Short Wave Infrared",
                    "eo: full_width_half_max": 0.18,
                    "name": "B12",
                },
            ],
            "size": 503032453,
        },
        "metadata": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_vmsk_sharp_rad_srefdem_stdsref_meta.xml",
            "roles": ["metadata"],
            "location": "on_disk",
            "size": 18461,
        },
        "saturated_pixels": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_sat.tif",
            "roles": ["data"],
            "location": "on_disk",
            "size": 1774631,
        },
        "thumbnail": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_vmsk_sharp_rad_srefdem_stdsref_thumbnail.jpg",
            "roles": ["thumbnail"],
            "location": "on_disk",
            "size": 28774,
        },
        "topographic_shadow": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_toposhad.tif",
            "roles": ["data"],
            "location": "on_disk",
            "size": 384619,
        },
        "valid_pixels": {
            "href": "https://dap.ceda.ac.uk/neodc/sentinel_ard/data/sentinel_2/2023/11/17/S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb_valid.tif",
            "roles": ["data"],
            "location": "on_disk",
            "size": 318874,
        },
    },
    "links": [
        {
            "href": "https://test.eodatahub.org.uk/api/catalogue/stac/catalogs/supported-datasets/ceda-stac-catalogue/collections/sentinel2_ard/items/neodc.sentinel_ard.data.sentinel_2.2023.11.17.S2A_20231117_latn546lonw0022_T30UWF_ORB137_20231117131218_utm30n_osgb",
            "rel": "self",
            "type": "application/geo+json",
        },
        {
            "href": "https://test.eodatahub.org.uk/api/catalogue/stac/catalogs/supported-datasets/ceda-stac-catalogue/collections/sentinel2_ard",
            "rel": "parent",
            "type": "application/json",
        },
        {
            "href": "https://test.eodatahub.org.uk/api/catalogue/stac/catalogs/supported-datasets/ceda-stac-catalogue/collections/sentinel2_ard",
            "rel": "collection",
            "type": "application/json",
        },
        {
            "href": "https://test.eodatahub.org.uk/api/catalogue/stac/catalogs/supported-datasets/ceda-stac-catalogue",
            "rel": "root",
            "type": "application/json",
        },
    ],
    "collection": "sentinel2_ard",
}


def crop(v: PositiveInt) -> PositiveInt:
    """Crop value to 10,000."""
    return min(v, 10_000)


Limit = Annotated[PositiveInt, AfterValidator(crop)]
Intersection = Union[  # noqa: UP007
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    GeometryCollection,
]
SearchDatetime = TypeAdapter(UtcDatetime | None)


class FetchItemResult(NamedTuple):
    collection: str
    items: list[dict[str, Any]]
    token: str | None = None


class SearchContext(BaseModel):
    limit: int
    returned: int


class StacSearchResponse(BaseModel):
    items: dict[str, Any] = Field(..., examples=[{"type": "FeatureCollection", "features": [EXAMPLE_FEATURE]}])
    continuation_tokens: dict[str, str | None] = Field(..., examples=[{"sentinel-2-l2a-ard": "MTcwMDIxOTYxMTAwMA=="}])
    context: SearchContext


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
    _start_date: dt.datetime | None = None
    _end_date: dt.datetime | None = None

    # Properties to return the private values
    @property
    def start_date(self) -> dt.datetime | None:
        return self._start_date

    @property
    def end_date(self) -> dt.datetime | None:
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
            "list[dt.datetime | None]",
            [
                # Use the type adapter to validate the datetime strings, strict is necessary
                # due to pydantic issues #8736 and #8762
                SearchDatetime.validate_strings(v, strict=True) if v else None
                for v in values
            ],
        )

        # If there is a start and end date, check that the start date is before the end date
        if dates[0] and dates[1] and dates[0] > dates[1]:
            msg = "Invalid datetime range. Begin date after end date. Must match format: {begin_date}/{end_date}"
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
