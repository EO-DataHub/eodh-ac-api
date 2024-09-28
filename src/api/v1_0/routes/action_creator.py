from __future__ import annotations

import uuid  # noqa: TCH003
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials  # noqa: TCH002
from starlette import status

from src.api.v1_0.routes.auth import decode_token, validate_access_token
from src.api.v1_0.schemas import (
    ActionCreatorFunctionSpec,
    ActionCreatorJob,
    ActionCreatorJobsResponse,
    ActionCreatorSubmissionRequest,
    FunctionsResponse,
)
from src.api.v1_0.schemas.action_creator import ActionCreatorJobSummary
from src.api.v1_0.schemas.functions import FUNCTION_TO_INPUTS_LOOKUP
from src.services.action_creator_repo import ActionCreatorRepository, get_function_repo  # noqa: TCH001
from src.services.ades.client import ades_client

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
            "description": "Collection Not found",
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
)
async def submit_function(
    creation_spec: ActionCreatorSubmissionRequest,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJob:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_client(workspace=username, token=credential.credentials)
    inputs_cls = FUNCTION_TO_INPUTS_LOOKUP[creation_spec.preset_function.function_identifier]
    validated_func_inputs = inputs_cls(**creation_spec.preset_function.inputs).as_ogc_process_inputs()
    response = await ades.execute_process(
        process_identifier=creation_spec.preset_function.function_identifier,
        process_inputs=validated_func_inputs,
    )
    return ActionCreatorJob(
        submission_id=response["jobID"],
        spec=creation_spec,
        status=response["status"],
        submitted_at=response["created"],
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
    ades_jobs = await ades.list_job_submissions()
    return ActionCreatorJobsResponse(
        submitted_jobs=[
            ActionCreatorJobSummary(
                submission_id=job["jobID"],
                function_identifier=job["processID"],
                status=job["status"],
                submitted_at=job["created"],
                finished_at=job.get("finished"),
            )
            for job in ades_jobs["jobs"]
        ],
        total=len(ades_jobs["jobs"]),
    )


@action_creator_router_v1_0.get(
    "/submissions/{submission_id}",
    response_model=ActionCreatorJobSummary,
    response_model_exclude_unset=False,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_function_submission_status(
    submission_id: uuid.UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJobSummary:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_client(workspace=username, token=credential.credentials)
    job = await ades.get_job_details(job_id=submission_id)
    return ActionCreatorJobSummary(
        submission_id=job["jobID"],
        function_identifier=job["processID"],
        status=job["status"],
        submitted_at=job["created"],
        finished_at=job["finished"],
    )


@action_creator_router_v1_0.delete(
    "/submissions/{correlation_id}",
    status_code=204,
    response_model=None,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def cancel_function_execution(
    correlation_id: uuid.UUID,  # noqa: ARG001
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Function execution cancellation is currently not implemented",
    )
