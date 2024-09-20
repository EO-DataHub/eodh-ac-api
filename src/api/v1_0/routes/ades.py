from __future__ import annotations

from typing import Annotated
from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials  # noqa: TCH002

from src.api.v1_0.routes.auth import decode_token, validate_access_token
from src.api.v1_0.schemas.ades import JobExecutionResults, JobList, Process, ProcessList, StatusInfo
from src.services.ades import ades_service

ades_router_v1_0 = APIRouter(
    prefix="/ades",
    tags=["ADES"],
)


@ades_router_v1_0.get(
    "/processes",
    response_model=ProcessList,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_my_processes(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ProcessList:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return ProcessList(**await ades.list_processes())


@ades_router_v1_0.get(
    "/processes/{name}",
    response_model=Process,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_process_details(
    name: str,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> Process:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return Process(**await ades.get_process_details(name))


@ades_router_v1_0.get(
    "/jobs",
    response_model=JobList,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_my_job_submissions(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> JobList:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return JobList(**await ades.list_job_submissions())


@ades_router_v1_0.get(
    "/jobs/{job_id}",
    response_model=StatusInfo,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_job_execution_details(
    job_id: str | UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> StatusInfo:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return StatusInfo(**await ades.get_job_details(job_id))


@ades_router_v1_0.get(
    "/jobs/{job_id}/results",
    response_model=JobExecutionResults,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_job_execution_results(
    job_id: str | UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> JobExecutionResults:
    introspected_token = await decode_token(credential)
    username = introspected_token["preferred_username"]
    ades = ades_service(workspace=username, token=credential.credentials)
    return JobExecutionResults(results=await ades.get_job_results(job_id))
