from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from enum import Enum
from typing import Any, Sequence

from pydantic import BaseModel, model_validator


class ActionCreatorJobStatus(str, Enum):
    submitted = "submitted"
    running = "running"
    cancel_request = "cancel-request"
    successful = "successful"
    failed = "failed"
    cancelled = "cancelled"


class ActionCreatorSubmissionRequest(BaseModel):
    function_name: str
    function_params: dict[str, Any]


class ActionCreatorJob(BaseModel):
    correlation_id: str
    spec: ActionCreatorSubmissionRequest
    status: ActionCreatorJobStatus = ActionCreatorJobStatus.submitted
    submitted_at: datetime
    running_at: datetime | None = None
    finished_at: datetime | None = None
    successful: bool | None = None


class ActionCreatorJobSummary(BaseModel):
    correlation_id: str
    status: ActionCreatorJobStatus
    function_name: str
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


class ActionCreatorJobsResponse(BaseModel):
    submitted_jobs: Sequence[ActionCreatorJobSummary]
    total: int
