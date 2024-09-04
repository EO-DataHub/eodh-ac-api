from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from enum import Enum
from typing import Any

from fastapi_hypermodel import FrozenDict, HALFor, HALLinks
from pydantic import UUID4, BaseModel


class ActionCreatorJobStatus(str, Enum):
    submitted = "submitted"
    running = "running"
    cancel_request = "cancel-request"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ActionCreatorSubmissionRequest(BaseModel):
    function_name: str
    function_params: dict[str, Any]


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
