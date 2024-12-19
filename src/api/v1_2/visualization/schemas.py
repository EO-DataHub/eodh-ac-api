from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, Field, PositiveInt
from stac_pydantic.api import Search
from stac_pydantic.api.extensions.fields import FieldsExtension  # noqa: TCH002
from stac_pydantic.api.extensions.query import Operator  # noqa: TCH002
from stac_pydantic.api.extensions.sort import SortExtension  # noqa: TCH002


def crop(v: PositiveInt) -> PositiveInt:
    """Crop value to 10,000."""
    return min(v, 10_000)


Limit = Annotated[PositiveInt, AfterValidator(crop)]


class StacSearch(Search):
    limit: Limit = Field(
        50,
        description="Limits the number of results that are included in each page of the response (capped to 10_000).",
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
    stac_query: dict[str, Any] | None = None


class ClassificationStackedBarChartRecord(BaseModel):
    name: str
    area: list[float]
    percentage: list[float]
    color_hint: str = Field(alias="color-hint")


class RangeAreaWithLineChartRecord(BaseModel):
    min: float
    max: float
    median: float
    x_label: datetime


class AssetChartVisualization(BaseModel):
    title: str
    units: str


class RangeAreaWithLineChartColors(BaseModel):
    line: str
    range_area: str


class RangeAreaWithLineChartVisualization(AssetChartVisualization):
    chart_type: Literal["range-area-with-line"] = "range-area-with-line"
    data: list[RangeAreaWithLineChartRecord]
    colors: RangeAreaWithLineChartColors


class ClassificationAssetChartVisualization(AssetChartVisualization):
    chart_type: Literal["classification-stacked-bar-chart"] = "classification-stacked-bar-chart"
    x_labels: list[datetime | str]
    data: list[ClassificationStackedBarChartRecord]


class JobAssetsChartVisualizationResponse(BaseModel):
    job_id: str
    assets: dict[
        str,
        Annotated[
            RangeAreaWithLineChartVisualization | ClassificationAssetChartVisualization,
            Field(discriminator="chart_type"),
        ],
    ]
