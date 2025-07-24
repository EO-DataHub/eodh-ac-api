from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum, auto
from typing import Annotated, Any, Literal, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

T = TypeVar("T", bound=BaseModel)
DEFAULT_PAGE_IDX = 1
MIN_PAGE_IDX = 1
DEFAULT_RESULTS_PER_PAGE = 25
MIN_RESULTS_PER_PAGE = 1
MAX_RESULTS_PER_PAGE = 100


class ActionCreatorJobStatus(StrEnum):
    submitted = auto()
    running = auto()
    cancel_request = "cancel-request"
    successful = auto()
    failed = auto()
    cancelled = auto()


class ActionCreatorJob(BaseModel):
    job_id: str
    workflow_spec: dict[str, Any]
    status: ActionCreatorJobStatus = ActionCreatorJobStatus.submitted
    submitted_at: datetime
    running_at: datetime | None = None
    finished_at: datetime | None = None
    successful: bool | None = None


class ActionCreatorJobSummary(BaseModel):
    job_id: str
    status: ActionCreatorJobStatus
    workflow_identifier: str
    submitted_at: datetime
    finished_at: datetime | None = None
    successful: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def resolve_job_success_flag(cls, v: dict[str, Any]) -> dict[str, Any]:
        status = v.get("status")
        if status is None:
            v["successful"] = None
        elif status == "failed":
            v["successful"] = False
        elif status == "successful":
            v["successful"] = True
        else:
            v["successful"] = None
        return v


class OrderDirection(StrEnum):
    asc = auto()
    desc = auto()


class ActionCreatorSubmissionsQueryParams(BaseModel):
    workspace: Annotated[str | None, Field(None, description="Workspace to query")]
    order_by: Annotated[
        Literal["job_id", "status", "workflow_identifier", "submitted_at", "finished_at", "successful"],
        Field("submitted_at", description="Field to use for ordering - `submitted_at` by default"),
    ]
    order_direction: Annotated[
        OrderDirection,
        Field("asc", description="Order direction - `asc` by default"),
    ]
    page: Annotated[
        int,
        Field(DEFAULT_PAGE_IDX, description="Page number - 1 by default", ge=MIN_PAGE_IDX),
    ]
    per_page: Annotated[
        int | None,
        Field(
            None,
            description="Number of results to return - all by default",
            ge=MIN_RESULTS_PER_PAGE,
        ),
    ]
    status: Annotated[
        list[ActionCreatorJobStatus],
        Field(
            default_factory=list,
            description="Filter by submission status",
        ),
    ]

    @classmethod
    @field_validator("order_by", mode="before")
    def validate_order_by(cls, v: str | None) -> str:
        return "submitted_at" if v is None else v

    @classmethod
    @field_validator("order_direction", mode="before")
    def validate_order_direction(cls, v: str | None) -> str:
        return "asc" if v is None else v

    @classmethod
    @field_validator("page", mode="before")
    def validate_page(cls, v: int | None) -> int:
        return DEFAULT_PAGE_IDX if v is None else v

    @classmethod
    @field_validator("per_page", mode="before")
    def validate_per_page(cls, v: int | None) -> int:
        return DEFAULT_RESULTS_PER_PAGE if v is None else v


class PaginationResults[T: BaseModel](BaseModel):
    results: Sequence[T]
    total_items: int
    current_page: int
    total_pages: int
    results_on_current_page: int
    results_per_page: int | None = None
    ordered_by: str
    order_direction: OrderDirection
