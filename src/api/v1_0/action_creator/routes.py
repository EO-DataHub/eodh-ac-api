from __future__ import annotations

import uuid  # noqa: TCH003
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials  # noqa: TCH002
from starlette import status

from src.api.v1_0.action_creator.schemas import (
    FUNCTION_TO_INPUTS_LOOKUP,
    ActionCreatorFunctionSpec,
    ActionCreatorJob,
    ActionCreatorJobsResponse,
    ActionCreatorJobSummary,
    ActionCreatorSubmissionRequest,
    ErrorResponse,
    FunctionsResponse,
)
from src.api.v1_0.auth.routes import decode_token, validate_access_token
from src.services.ades.client import ades_client
from src.services.db.action_creator_repo import ActionCreatorRepository, get_function_repo  # noqa: TCH001

action_creator_router_v1_0 = APIRouter(
    prefix="/action-creator",
    tags=["Action Creator"],
)


@action_creator_router_v1_0.get(
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
    repo: Annotated[ActionCreatorRepository, Depends(get_function_repo)],
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
    collection: Annotated[str | None, Query(max_length=64, description="STAC collection")] = None,
) -> FunctionsResponse:
    collection_supported_flag, results = repo.get_available_functions(collection)
    if not collection_supported_flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection does not exist or is not supported by Action Creator",
        )
    return FunctionsResponse(functions=[ActionCreatorFunctionSpec(**f) for f in results], total=len(results))


@action_creator_router_v1_0.post(
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
async def submit_function(
    creation_spec: ActionCreatorSubmissionRequest,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJob:
    introspected_token = await decode_token(credential)

    if creation_spec.preset_function.function_identifier not in FUNCTION_TO_INPUTS_LOOKUP:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function '{creation_spec.preset_function.function_identifier}' not found. "
            "Please use `/functions` endpoint to get list of supported functions.",
        )

    username = introspected_token["preferred_username"]
    ades = ades_client(workspace=username, token=credential.credentials)

    inputs_cls = FUNCTION_TO_INPUTS_LOOKUP[creation_spec.preset_function.function_identifier]
    inputs = inputs_cls(**creation_spec.preset_function.inputs).as_ogc_process_inputs()

    err, response = await ades.execute_process(
        process_identifier=creation_spec.preset_function.function_identifier,
        process_inputs=inputs,
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
        spec=creation_spec,
        status=response.status.value,
        submitted_at=response.created,
    )


@action_creator_router_v1_0.get(
    "/submissions",
    response_model=ActionCreatorJobsResponse,
    response_model_exclude_unset=False,
    response_model_exclude_none=False,
    status_code=status.HTTP_200_OK,
)
async def get_function_submissions(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJobsResponse:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_client(workspace=username, token=credential.credentials)
    err, ades_jobs = await ades.list_job_submissions()

    if err is not None:
        raise HTTPException(status_code=err.code, detail=err.detail)

    if ades_jobs is None:  # Impossible case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing preset function",
        )

    return ActionCreatorJobsResponse(
        submitted_jobs=[
            ActionCreatorJobSummary(
                submission_id=job.job_id,
                function_identifier=job.process_id,
                status=job.status.value,
                submitted_at=job.created,
                finished_at=job.finished,
            )
            for job in ades_jobs.jobs
        ],
        total=len(ades_jobs.jobs),  # Use len() as ADES returns count for the unregistered processes too
    )


@action_creator_router_v1_0.get(
    "/submissions/{submission_id}",
    response_model=ActionCreatorJobSummary,
    response_model_exclude_unset=False,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": ErrorResponse}},
)
async def get_function_submission_status(
    submission_id: uuid.UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJobSummary:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_client(workspace=username, token=credential.credentials)
    err, job = await ades.get_job_details(job_id=submission_id)

    if err:
        raise HTTPException(status_code=err.code, detail=err.detail)

    if job is None:
        # This should never happen if error was not generated
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return ActionCreatorJobSummary(
        submission_id=job.job_id,
        function_identifier=job.process_id,
        status=job.status.value,
        submitted_at=job.created,
        finished_at=job.finished,
    )


@action_creator_router_v1_0.delete(
    "/submissions/{submission_id}",
    status_code=204,
    response_model=None,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": ErrorResponse}},
)
async def cancel_function_execution(
    submission_id: uuid.UUID,  # noqa: ARG001
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Function execution cancellation is currently not implemented",
    )
