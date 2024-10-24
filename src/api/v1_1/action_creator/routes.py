from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials  # noqa: TCH002
from starlette import status

from src.api.v1_0.auth.routes import decode_token, validate_access_token
from src.api.v1_1.action_creator.schemas.errors import ErrorResponse
from src.api.v1_1.action_creator.schemas.functions import FunctionsResponse
from src.api.v1_1.action_creator.schemas.history import ActionCreatorJob
from src.api.v1_1.action_creator.schemas.presets import LAND_COVER_CHANGE_DETECTION_PRESET, PresetList
from src.api.v1_1.action_creator.schemas.workflow_steps import (
    WorkflowStepsResponse,
)
from src.api.v1_1.action_creator.schemas.workflows import WorkflowSpec  # noqa: TCH001
from src.utils.logging import get_logger

_logger = get_logger(__name__)

action_creator_router_v1_1 = APIRouter(
    prefix="/action-creator",
    tags=["Action Creator"],
)


@action_creator_router_v1_1.get(
    "/functions",
    response_model=FunctionsResponse,
    response_model_exclude_unset=False,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def get_available_functions(
    dataset: Annotated[str | None, Query(max_length=64, description="Dataset")] = None,  # noqa: ARG001
) -> FunctionsResponse:
    return FunctionsResponse(functions=[], total=0)


@action_creator_router_v1_1.get(
    "/presets",
    response_model=PresetList,
    response_model_exclude_unset=False,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def get_available_presets() -> PresetList:
    return PresetList(presets=[LAND_COVER_CHANGE_DETECTION_PRESET], total=0)


@action_creator_router_v1_1.get(
    "/workflow-steps",
    response_model=WorkflowStepsResponse,
    response_model_exclude_unset=False,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def get_workflow_step_specifications() -> WorkflowStepsResponse:
    return WorkflowStepsResponse(steps=[], total=0)


@action_creator_router_v1_1.post(
    "/workflow-submissions",
    response_model=ActionCreatorJob,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def submit_workflow(
    workflow_spec: WorkflowSpec,  # noqa: ARG001
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJob:
    _ = decode_token(credential.credentials)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )
