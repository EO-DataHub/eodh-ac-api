from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession
from aiohttp_retry import ExponentialRetry, RetryClient
from pydantic import BaseModel
from starlette import status

from src.consts.action_creator import FUNCTIONS_REGISTRY
from src.core.settings import current_settings
from src.services.ades.schemas import JobList, Process, ProcessList, ProcessSummary, StatusInfo
from src.utils.logging import get_logger

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path
    from uuid import UUID


class ErrorResponse(BaseModel):
    code: int
    detail: str | dict[str, Any] | None = None


class ADESClient:
    def __init__(
        self,
        url: str,
        ogc_processes_api_path: str,
        ogc_jobs_api_path: str,
        workspace: str,
        token: str,
        logger: Logger,
    ) -> None:
        self.ogc_jobs_api_path = ogc_jobs_api_path
        self.ogc_processes_api_path = ogc_processes_api_path
        self.logger = logger
        self.token = token
        self.workspace = workspace
        self.url = url
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    @property
    def processes_endpoint_url(self) -> str:
        return f"{self.url.strip('/')}/{self.workspace}/{self.ogc_processes_api_path}"

    @property
    def jobs_endpoint_url(self) -> str:
        return f"{self.url.strip('/')}/{self.workspace}/{self.ogc_jobs_api_path}"

    def _get_retry_client(self) -> tuple[ClientSession, RetryClient]:
        client_session = ClientSession()
        exp_retry = ExponentialRetry(
            attempts=5,
            statuses={
                status.HTTP_429_TOO_MANY_REQUESTS,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                status.HTTP_502_BAD_GATEWAY,
                status.HTTP_503_SERVICE_UNAVAILABLE,
            },
        )
        retry_client = RetryClient(
            client_session=client_session,
            retry_options=exp_retry,
            logger=self.logger,
        )
        return client_session, retry_client

    async def get_job_details(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.jobs_endpoint_url}/{job_id}",
                headers=self.headers,
            ) as response:
                # ADES returns 403 when getting non-existent job
                if response.status == status.HTTP_403_FORBIDDEN:
                    return ErrorResponse(code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' does not exist."), None
                return None, StatusInfo(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def get_job_results(self, job_id: str | UUID) -> dict[str, Any]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.jobs_endpoint_url}/{job_id}/results",
                headers=self.headers,
                raise_for_status=True,
            ) as response:
                return await response.json()  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def list_job_submissions(self) -> JobList:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=self.jobs_endpoint_url,
                headers=self.headers,
                raise_for_status=True,
            ) as response:
                return JobList(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def cancel_job(self, job_id: str | UUID) -> ErrorResponse | None:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.delete(
                url=f"{self.jobs_endpoint_url}/{job_id}",
                headers=self.headers,
            ) as response:
                # ADES returns 403 when cancelling non-existent job
                if response.status == status.HTTP_403_FORBIDDEN:
                    return ErrorResponse(code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' does not exist.")
                if response.status == status.HTTP_501_NOT_IMPLEMENTED:
                    return ErrorResponse(
                        code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail="Job cancellation is not implemented.",
                    )
                response.raise_for_status()
                return None
        finally:
            await client_session.close()

    async def register_process_from_cwl_href(self, cwl_href: str) -> ProcessSummary:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.post(
                url=self.processes_endpoint_url,
                headers=self.headers,
                raise_for_status=True,
                json={"executionUnit": {"href": cwl_href, "type": "application/cwl"}},
            ) as response:
                return ProcessSummary(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def register_process_from_local_cwl_file(self, cwl_location: Path) -> ProcessSummary:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.post(
                url=self.processes_endpoint_url,
                headers=self.headers | {"Content-Type": "application/cwl+yaml"},
                raise_for_status=True,
                data=cwl_location.read_bytes(),
            ) as response:
                return ProcessSummary(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def process_exists(self, process_identifier: str) -> bool:
        user_processes = await self.list_processes()
        return process_identifier in {p.id for p in user_processes.processes}

    async def ensure_process_exists(self, process_identifier: str) -> None:
        if await self.process_exists(process_identifier):
            return
        cwl_href = FUNCTIONS_REGISTRY[process_identifier]["cwl_href"]
        await self.register_process_from_cwl_href(cwl_href=cwl_href)

    async def list_processes(self) -> ProcessList:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=self.processes_endpoint_url,
                headers=self.headers,
                raise_for_status=True,
            ) as response:
                return ProcessList(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def get_process_details(self, process_identifier: str) -> Process:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.processes_endpoint_url}/{process_identifier}",
                headers=self.headers,
            ) as response:
                return Process(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def execute_process(self, process_identifier: str, process_inputs: dict[str, Any]) -> StatusInfo:
        client_session, retry_client = self._get_retry_client()
        try:
            if "inputs" not in process_inputs:
                process_inputs = {"inputs": process_inputs}

            if "workspace" not in process_inputs["inputs"]:
                process_inputs["inputs"]["workspace"] = self.workspace

            async with retry_client.post(
                url=f"{self.processes_endpoint_url}/{process_identifier}/execution",
                headers=self.headers | {"Content-Type": "application/json", "Prefer": "respond-async"},
                json=process_inputs,
            ) as response:
                return StatusInfo(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def get_process_executions(self, name: str) -> JobList:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.processes_endpoint_url}/{name}/jobs",
                headers=self.headers,
                raise_for_status=True,
            ) as response:
                return JobList(**await response.json())  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def unregister_process(self, process_identifier: str) -> None:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.delete(
                url=f"{self.processes_endpoint_url}/{process_identifier}",
                headers=self.headers,
                raise_for_status=True,
            ):
                return
        finally:
            await client_session.close()

    async def reregister_process(self, process_identifier: str) -> ProcessSummary:
        if await self.process_exists(process_identifier):
            await self.unregister_process(process_identifier)
        cwl_href = FUNCTIONS_REGISTRY[process_identifier]["cwl_href"]
        return await self.register_process_from_cwl_href(cwl_href)


def ades_client(workspace: str, token: str) -> ADESClient:
    settings = current_settings()
    return ADESClient(
        url=settings.ades.url,
        ogc_processes_api_path=settings.ades.ogc_processes_api_path,
        ogc_jobs_api_path=settings.ades.ogc_jobs_api_path,
        workspace=workspace,
        logger=get_logger(__name__),
        token=token,
    )
