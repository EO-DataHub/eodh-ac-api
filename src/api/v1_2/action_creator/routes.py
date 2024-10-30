from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from src.api.v1_0.auth.routes import decode_token, validate_access_token
from src.api.v1_2.action_creator.schemas.errors import ErrorResponse
from src.api.v1_2.action_creator.schemas.functions import FunctionsResponse
from src.api.v1_2.action_creator.schemas.history import ActionCreatorJob
from src.api.v1_2.action_creator.schemas.presets import (
    ERR_AOI_TOO_BIG_NDVI_WORKFLOW_SPEC,
    ERR_INVALID_DATASET_NDVI_WORKFLOW_SPEC,
    ERR_INVALID_DATE_RANGE_NDVI_WORKFLOW_SPEC,
    ERR_INVALID_REF_PATH_WORKFLOW_SPEC,
    NDVI_WORKFLOW_SPEC,
    PRESET_LOOKUP,
    PRESETS,
    SIMPLEST_NDVI_WORKFLOW_SPEC,
    PresetList,
)
from src.api.v1_2.action_creator.schemas.workflow_steps import (
    FUNCTIONS,
    WorkflowValidationResult,
)
from src.api.v1_2.action_creator.schemas.workflows import WorkflowSpec
from src.utils.logging import get_logger

_logger = get_logger(__name__)

TWorkflowSpec = Annotated[
    WorkflowSpec,
    Body(
        openapi_examples={
            "land-cover-change-preset": {
                "summary": "OK - Land Cover Change Detection",
                "description": "Land Cover Change Detection using ESA LCCCI Global Land Cover Map.",
                "value": PRESET_LOOKUP["lulc-change"]["workflow"],
            },
            "water-quality-preset": {
                "summary": "OK - Water Quality with in-situ data calibration",
                "description": "Calculate Cyanobacteria Index for Water Quality verification "
                "with in-situ data calibration.",
                "value": PRESET_LOOKUP["water-quality"]["workflow"],
            },
            "simplest-workflow-ndvi": {
                "summary": "OK - Simplest possible Workflow - NDVI",
                "description": "Get S2 data and calculate NDVI only",
                "value": SIMPLEST_NDVI_WORKFLOW_SPEC,
            },
            "ndvi-clip-reproject": {
                "summary": "OK - NDVI with AOI clipping and reprojection",
                "description": "Calculate NDVI and clip the results to selected Area",
                "value": NDVI_WORKFLOW_SPEC,
            },
            "err-ndvi-area-too-big": {
                "summary": "Error - Area too big",
                "value": ERR_AOI_TOO_BIG_NDVI_WORKFLOW_SPEC,
            },
            "err-ndvi-invalid-date-range": {
                "summary": "Error - Invalid date range",
                "value": ERR_INVALID_DATE_RANGE_NDVI_WORKFLOW_SPEC,
            },
            "err-ndvi-invalid-dataset": {
                "summary": "Error - Dataset not supported for this function",
                "value": ERR_INVALID_DATASET_NDVI_WORKFLOW_SPEC,
            },
            "err-ndvi-invalid-reference": {
                "summary": "Error - Invalid input reference path",
                "value": ERR_INVALID_REF_PATH_WORKFLOW_SPEC,
            },
        },
    ),
]

action_creator_router_v1_2 = APIRouter(
    prefix="/action-creator",
    tags=["Action Creator"],
)


@action_creator_router_v1_2.get(
    "/functions",
    response_model=FunctionsResponse,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def get_available_functions(
    dataset: Annotated[str | None, Query(max_length=64, description="Dataset")] = None,
) -> FunctionsResponse:
    funcs = [f for f in FUNCTIONS if f["visible"]]
    if dataset:
        funcs = [f for f in funcs if dataset in f["compatible_input_datasets"]]
    return FunctionsResponse(functions=funcs, total=len(funcs))


@action_creator_router_v1_2.get(
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
    return PresetList(presets=PRESETS, total=len(PRESETS))


@action_creator_router_v1_2.post(
    "/workflow-validation",
    response_model=WorkflowValidationResult,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def validate_workflow_specification(workflow_spec: TWorkflowSpec) -> WorkflowValidationResult:  # noqa: ARG001
    return WorkflowValidationResult(valid=True)


@action_creator_router_v1_2.post(
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
    workflow_spec: TWorkflowSpec,  # noqa: ARG001
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJob:
    _ = decode_token(credential.credentials)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )
