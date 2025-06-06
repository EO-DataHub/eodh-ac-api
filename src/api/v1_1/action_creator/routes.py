from __future__ import annotations

import math
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from src.api.v1_0.auth.routes import decode_token, validate_access_token
from src.api.v1_1.action_creator.functions import (
    FUNCTION_IDENTIFIER_TO_WORKFLOW_MAPPING,
    FUNCTIONS,
    WORKFLOW_ID_OVERRIDE_LOOKUP,
    WORKFLOW_REGISTRY,
)
from src.api.v1_1.action_creator.presets import (
    LAND_COVER_CHANGE_DETECTION_PRESET_SPEC,
    NDVI_CLIP_PRESET,
    NDVI_PRESET,
    PRESETS,
    WATER_QUALITY_PRESET,
)
from src.api.v1_1.action_creator.schemas import (
    ActionCreatorJob,
    ActionCreatorJobSummary,
    ActionCreatorSubmissionRequest,
    ActionCreatorSubmissionsQueryParams,
    ErrorResponse,
    FunctionsResponse,
    PaginationResults,
    PresetsResponse,
)
from src.services.ades.factory import ades_client_factory
from src.services.ades.schemas import StatusCode
from src.utils.logging import get_logger

_logger = get_logger(__name__)

TWorkflowCreationSpec = Annotated[
    ActionCreatorSubmissionRequest,
    Body(
        openapi_examples={
            "land-cover-change-preset": {
                "summary": "Land Cover Change Detection",
                "description": "Land Cover Change Detection using ESA LCCCI Global Land Cover Map.",
                "value": {"workflow": LAND_COVER_CHANGE_DETECTION_PRESET_SPEC["workflow"]},
            },
            "simplest-ndvi": {
                "summary": "Simplest workflow - NDVI",
                "description": "Just an NDVI function",
                "value": NDVI_PRESET,
            },
            "ndvi+clip": {
                "summary": "NDVI with Clipping",
                "description": "NDVI function with additional Clipping of the results",
                "value": NDVI_CLIP_PRESET,
            },
            "water-quality": {
                "summary": "Water Quality",
                "description": "Water quality analysis",
                "value": WATER_QUALITY_PRESET,
            },
        }
    ),
]

action_creator_router_v1_1 = APIRouter(
    prefix="/action-creator",
    tags=["Action Creator"],
)


@action_creator_router_v1_1.get(
    "/functions",
    response_model=FunctionsResponse,
    response_model_exclude_unset=False,
    response_model_exclude_none=True,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def get_available_functions(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
    collection: Annotated[str | None, Query(max_length=64, description="STAC collection")] = None,
) -> FunctionsResponse:
    funcs = [f for f in FUNCTIONS if f["visible"]]
    if collection:
        funcs = [f for f in funcs if collection in f["compatible_input_datasets"]]  # type: ignore[operator]
    return FunctionsResponse(functions=funcs, total=len(funcs))


@action_creator_router_v1_1.get(
    "/presets",
    response_model=PresetsResponse,
    response_model_exclude_unset=False,
    response_model_exclude_none=True,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def get_available_presets(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
) -> PresetsResponse:
    presets = [p for p in PRESETS if p["visible"]]  # type: ignore[index]
    return PresetsResponse(presets=presets, total=len(presets))


@action_creator_router_v1_1.post(
    "/submissions",
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
    workflow_spec: TWorkflowCreationSpec,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJob:
    introspected_token = decode_token(credential.credentials)

    ades = ades_client_factory(workspace=introspected_token["preferred_username"], token=credential.credentials)

    workflow_step_spec = next(iter(workflow_spec.workflow.values()))
    wf_identifier = FUNCTION_IDENTIFIER_TO_WORKFLOW_MAPPING[workflow_step_spec.identifier]
    ogc_inputs = workflow_step_spec.inputs.as_ogc_process_inputs()
    ogc_inputs["clip"] = (
        "True" if any(step.identifier == "clip" for step in workflow_spec.workflow.values()) else "False"
    )

    err, _ = await ades.reregister_process_v2(
        wf_identifier,
        wf_registry=WORKFLOW_REGISTRY,
        wf_id_override_lookup=WORKFLOW_ID_OVERRIDE_LOOKUP,
    )

    if err is not None:
        raise HTTPException(
            status_code=err.code,
            detail=err.detail,
        )

    err, response = await ades.execute_process(
        process_identifier=wf_identifier,
        process_inputs=ogc_inputs,
    )

    if err is not None:  # Will happen if there are race conditions and the process was deleted or ADES is unresponsive
        raise HTTPException(
            status_code=err.code,
            detail=err.detail,
        )

    if response is None:  # Impossible case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing preset function",
        )

    return ActionCreatorJob(
        submission_id=response.job_id,
        spec=workflow_spec,
        status=response.status.value,
        submitted_at=response.created,
    )


@action_creator_router_v1_1.get(
    "/submissions",
    response_model=PaginationResults[ActionCreatorJobSummary],
    response_model_exclude_unset=False,
    response_model_exclude_none=False,
    status_code=status.HTTP_200_OK,
)
async def get_job_history(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
    params: Annotated[ActionCreatorSubmissionsQueryParams, Query(...)],
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
            "successful": True if job["status"] == "successful" else False if job["status"] == "failed" else None,
        }
        for job in ades_jobs["jobs"]
        if (params.status and job["status"] in params.status) or not params.status
    ]

    # Order by
    # Use tuples to handle None items - tuples are sorted item by item
    results.sort(
        key=lambda x: (x[params.order_by] is None, x[params.order_by]),
        reverse=params.order_direction == "desc",
    )

    # Paginate
    offset = (params.page - 1) * params.per_page if params.per_page else 0
    total_pages = math.ceil(len(results) / params.per_page) if params.per_page else 1 if results else 0
    limited_jobs = results[offset : offset + params.per_page] if params.per_page else results

    return {
        "results": limited_jobs,
        "total_items": len(results),  # Use len() as ADES returns count for the unregistered processes too
        "total_pages": total_pages,
        "ordered_by": params.order_by,
        "order_direction": params.order_direction,
        "current_page": params.page,
        "results_on_current_page": len(limited_jobs),
        "results_per_page": params.per_page,
    }


@action_creator_router_v1_1.get(
    "/submissions/{submission_id}",
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
        function_identifier=job.process_id,
        status=job.status if job.status != StatusCode.dismissed else "cancelled",
        submitted_at=job.created,
        finished_at=job.finished,
    )


@action_creator_router_v1_1.delete(
    "/submissions/{submission_id}",
    status_code=204,
    response_model=None,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": ErrorResponse}},
)
async def cancel_or_delete_job(
    submission_id: uuid.UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> None:
    introspected_token = decode_token(credential.credentials)
    username = introspected_token["preferred_username"]
    ades = ades_client_factory(workspace=username, token=credential.credentials)
    err, _ = await ades.cancel_or_delete_job(submission_id)
    if err:
        raise HTTPException(status_code=err.code, detail=err.detail)
