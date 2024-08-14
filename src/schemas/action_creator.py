from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from enum import Enum

from fastapi_hypermodel import FrozenDict, HALFor, HALHyperModel, HALLinks
from geojson_pydantic import Polygon  # noqa: TCH002
from pydantic import UUID4, BaseModel, Field


class ActionCreatorJobStatus(str, Enum):
    submitted = "submitted"
    running = "running"
    cancel_request = "cancel-request"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ActionCreatorFunction(str, Enum):
    evi = "EVI"
    ndvi = "NDVI"
    ndwi = "NDWI"
    savi = "SAVI"


class ActionCreatorSubmissionRequest(BaseModel):
    collection: str
    date_range_start: datetime
    date_range_end: datetime
    aoi: Polygon
    function: ActionCreatorFunction = ActionCreatorFunction.ndvi


class ActionCreatorJob(BaseModel):
    correlation_id: UUID4
    spec: ActionCreatorSubmissionRequest
    status: ActionCreatorJobStatus = ActionCreatorJobStatus.submitted
    submitted_at: datetime
    running_at: datetime | None = None
    finished_at: datetime | None = None
    cancelled_at: datetime | None = None
    successful: bool | None = None

    links: HALLinks = FrozenDict({
        "self": HALFor("get_status", {"correlation_id": "<correlation_id>"}),
        "cancel": HALFor("cancel", {"correlation_id": "<correlation_id>"}),
    })


class CollectionFunctions(BaseModel):
    collection: str
    functions: list[ActionCreatorFunction] = Field(default_factory=list, alias="functions")


class FunctionCollection(HALHyperModel):
    functions: list[CollectionFunctions]

    links: HALLinks = FrozenDict({
        "self": HALFor("get_available_functions"),
    })
