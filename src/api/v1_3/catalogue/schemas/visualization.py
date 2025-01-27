from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from src.api.v1_3.catalogue.schemas.stac_search import ExtendedStacSearch


class ClassificationStackedBarChartRecord(BaseModel):
    name: str
    area: list[float]
    percentage: list[float]
    color_hint: str = Field(alias="color-hint")


class RangeAreaWithLineChartRecord(BaseModel):
    min: float | None = None
    max: float | None = None
    median: float | None = None
    x_label: datetime


class AssetChartVisualization(BaseModel):
    title: str
    units: str


class RangeAreaWithLineChartVisualization(AssetChartVisualization):
    chart_type: Literal["range-area-with-line"] = "range-area-with-line"
    data: list[RangeAreaWithLineChartRecord]
    color: str = "#000000"


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


class VisualizationRequest(BaseModel):
    assets: list[str] | None = None
    stac_query: ExtendedStacSearch | None = None
