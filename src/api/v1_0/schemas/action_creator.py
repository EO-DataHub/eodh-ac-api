from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from enum import Enum
from typing import Any, Sequence

from pydantic import BaseModel, Field, model_validator


class ActionCreatorJobStatus(str, Enum):
    submitted = "submitted"
    running = "running"
    cancel_request = "cancel-request"
    successful = "successful"
    failed = "failed"
    cancelled = "cancelled"


class PresetFunctionExecutionRequest(BaseModel):
    function_identifier: str = Field(..., examples=["raster-calculate", "lulc-change"])
    inputs: dict[str, Any] = Field(
        ...,
        examples=[
            {
                "stac_collection": "sentinel-2-l2a",
                "aoi": '{"type": "Polygon","coordinates": [[[14.763294437090849, 50.833598186651244],'
                "[15.052268923898112, 50.833598186651244],[15.052268923898112, 50.989077215056824],"
                "[14.763294437090849, 50.989077215056824],[14.763294437090849, 50.833598186651244]]]}",
                "date_start": "2024-04-03T00:00:00",
                "date_end": "2024-08-01T00:00:00",
                "index": "NDVI",
            }
        ],
    )


class ActionCreatorSubmissionRequest(BaseModel):
    preset_function: PresetFunctionExecutionRequest


class ActionCreatorJob(BaseModel):
    submission_id: str
    spec: ActionCreatorSubmissionRequest
    status: ActionCreatorJobStatus = ActionCreatorJobStatus.submitted
    submitted_at: datetime
    running_at: datetime | None = None
    finished_at: datetime | None = None
    successful: bool | None = None


class ActionCreatorJobSummary(BaseModel):
    submission_id: str
    status: ActionCreatorJobStatus
    function_identifier: str
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
