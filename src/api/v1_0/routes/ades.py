from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials  # noqa: TCH002

from src.api.v1_0.routes.auth import decode_token, validate_access_token
from src.api.v1_0.schemas.ades import AdesJobSubmissionsResponse, AdesProcessDetailsResponse, AdesProcessesResponse
from src.services.ades import ades_service

ades_router_v1_0 = APIRouter(
    prefix="/ades",
    tags=["ADES"],
)


@ades_router_v1_0.get(
    "/processes",
    response_model=AdesProcessesResponse,
    response_model_exclude_unset=True,
)
async def get_my_processes(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> AdesProcessesResponse:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return AdesProcessesResponse(**await ades.list_processes())


@ades_router_v1_0.get(
    "/processes/{name}",
    response_model=AdesProcessDetailsResponse,
    response_model_exclude_unset=True,
)
async def get_process_details(
    name: str,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> AdesProcessDetailsResponse:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return AdesProcessDetailsResponse(**await ades.get_process_details(name))


@ades_router_v1_0.get(
    "/jobs",
    response_model=AdesJobSubmissionsResponse,
    response_model_exclude_unset=True,
)
async def get_my_job_submissions(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> AdesJobSubmissionsResponse:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return AdesJobSubmissionsResponse(**await ades.list_job_submissions())


@ades_router_v1_0.get(
    "/jobs/{job_id}",
    response_model_exclude_unset=True,
)
async def get_job_execution_details(
    job_id: str | UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> Any:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return await ades.get_job_details(job_id)


@ades_router_v1_0.get(
    "/jobs/{job_id}/results",
    response_model_exclude_unset=True,
)
async def get_job_execution_results(
    job_id: str | UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> Any:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return await ades.get_job_results(job_id)
