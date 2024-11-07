from __future__ import annotations

import math
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from src.api.v1_0.auth.routes import decode_token, validate_access_token
from src.api.v1_2.action_creator.schemas.errors import ErrorResponse
from src.api.v1_2.action_creator.schemas.functions import FunctionsResponse
from src.api.v1_2.action_creator.schemas.history import (
    ActionCreatorJob,
    ActionCreatorJobSummary,
    ActionCreatorSubmissionsQueryParams,
    PaginationResults,
)
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
from src.api.v1_2.action_creator.schemas.workflow_tasks import (
    FUNCTIONS,
    WorkflowValidationResult,
)
from src.api.v1_2.action_creator.schemas.workflows import WorkflowSpec
from src.services.ades.factory import ades_client_factory
from src.services.ades.schemas import StatusCode
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


@action_creator_router_v1_2.get(
    "/submissions",
    response_model=PaginationResults[ActionCreatorJobSummary],
    response_model_exclude_unset=False,
    response_model_exclude_none=False,
    status_code=status.HTTP_200_OK,
)
async def get_job_history(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
    params: Annotated[ActionCreatorSubmissionsQueryParams, Query()],
) -> dict[str, Any]:
    introspected_token = decode_token(credential.credentials)
    username = introspected_token["preferred_username"]
    ades = ades_client_factory(workspace=username, token=credential.credentials)

    # Get the jobs
    ades_jobs: dict[str, Any]
    err, ades_jobs = await ades.list_job_submissions(raw_output=True)  # type: ignore[assignment]

    if err is not None:
        raise HTTPException(status_code=err.code, detail=err.detail)

    if ades_jobs is None:  # Impossible case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing preset function",
        )

    # To result schema
    results = [
        {
            "submission_id": job["jobID"],
            "function_identifier": job["processID"],
            "status": job["status"],
            "submitted_at": job["created"],
            "finished_at": job.get("finished"),
            "successful": job["status"] == "successful",
        }
        for job in ades_jobs["jobs"]
    ]

    # Order by
    # Use tuples to handle None items - tuples are sorted item by item
    results.sort(
        key=lambda x: (x[params.order_by] is None, x[params.order_by]),
        reverse=params.order_direction == "desc",
    )

    # Paginate
    offset = (params.page - 1) * params.per_page
    total_pages = math.ceil(len(ades_jobs["jobs"]) / params.per_page)
    limited_jobs = results[offset : offset + params.per_page]

    return {
        "results": limited_jobs,
        "total_items": len(ades_jobs["jobs"]),  # Use len() as ADES returns count for the unregistered processes too
        "total_pages": total_pages,
        "ordered_by": params.order_by,
        "order_direction": params.order_direction,
        "current_page": params.page,
        "results_on_current_page": len(limited_jobs),
        "results_per_page": params.per_page,
    }


@action_creator_router_v1_2.get(
    "/workflow-submissions/{submission_id}",
    response_model=ActionCreatorJobSummary,
    response_model_exclude_unset=False,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": ErrorResponse}},
)
async def get_job_status(
    submission_id: uuid.UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJobSummary:
    introspected_token = decode_token(credential.credentials)
    username = introspected_token["preferred_username"]
    ades = ades_client_factory(workspace=username, token=credential.credentials)
    err, job = await ades.get_job_details(job_id=submission_id)

    if err:
        raise HTTPException(status_code=err.code, detail=err.detail)

    if job is None:
        # This should never happen if error was not generated
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return ActionCreatorJobSummary(
        submission_id=job.job_id,
        workflow_identifier=job.process_id,
        status=job.status if job.status != StatusCode.dismissed else "cancelled",
        submitted_at=job.created,
        finished_at=job.finished,
    )


@action_creator_router_v1_2.delete(
    "/workflow-submissions/{job_id}",
    status_code=204,
    response_model=None,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": ErrorResponse}},
)
async def cancel_or_delete_job(
    job_id: uuid.UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> None:
    introspected_token = decode_token(credential.credentials)
    username = introspected_token["preferred_username"]
    ades = ades_client_factory(workspace=username, token=credential.credentials)
    err, _ = await ades.cancel_job(job_id)
    if err:
        raise HTTPException(status_code=err.code, detail=err.detail)
