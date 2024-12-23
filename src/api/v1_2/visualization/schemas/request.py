from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, Field, PositiveInt
from stac_pydantic.api import Search
from stac_pydantic.api.extensions.query import Operator
from stac_pydantic.api.extensions.sort import SortExtension


def crop(v: PositiveInt) -> PositiveInt:
    """Crop value to 10,000."""
    return min(v, 10_000)


Limit = Annotated[PositiveInt, AfterValidator(crop)]


class FieldsExtension(BaseModel):
    include: set[str] = Field(None)
    exclude: set[str] = Field(None)


class StacSearch(Search):
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
    filter: dict[str, Any] | None = Field(
        default=None,
        description="A CQL filter expression for filtering items.",
        json_schema_extra={
            "example": {
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "id"},
                            "LC08_L1TP_060247_20180905_20180912_01_T1_L1TP",
                        ],
                    },
                    {"op": "=", "args": [{"property": "collection"}, "landsat8_l1tp"]},
                ],
            },
        },
    )
    filter_lang: Literal["cql-json", "cql2-json"] | None = Field(
        alias="filter-lang",
        default="cql2-json",
        description="The CQL filter encoding that the 'filter' value uses.",
    )


class VisualizationRequest(BaseModel):
    assets: list[str] | None = None
    stac_query: StacSearch | None = None
