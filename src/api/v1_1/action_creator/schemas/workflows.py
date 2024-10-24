from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from geojson_pydantic import Polygon  # noqa: TCH002
from pydantic import BaseModel

from src.api.v1_1.action_creator.schemas.workflow_steps import TWorkflowStep  # noqa: TCH001


class MainWorkflowInputs(BaseModel):
    area: Polygon
    date_start: datetime | None = None
    date_end: datetime | None = None
    dataset: str
    dataset_advanced_settings: dict[str, int | float | str | bool | None] | None = None


class WorkflowSpec(BaseModel):
    inputs: MainWorkflowInputs
    functions: dict[str, TWorkflowStep]


class WorkflowSubmissionRequest(BaseModel):
    workflow: WorkflowSpec
