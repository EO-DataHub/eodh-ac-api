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

    from aiohttp.client_exceptions import ClientResponse


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
            max_timeout=10,
            statuses={
                status.HTTP_429_TOO_MANY_REQUESTS,
                status.HTTP_502_BAD_GATEWAY,
                status.HTTP_503_SERVICE_UNAVAILABLE,
            },
            start_timeout=2,
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

                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                return None, StatusInfo(**await response.json())
        finally:
            await client_session.close()

    async def get_job_results(self, job_id: str | UUID) -> tuple[ErrorResponse | None, dict[str, Any] | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.jobs_endpoint_url}/{job_id}/results",
                headers=self.headers,
            ) as response:
                # ADES returns 403 when getting non-existent job
                if response.status == status.HTTP_403_FORBIDDEN:
                    return ErrorResponse(code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' does not exist."), None

                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                return None, await response.json()
        finally:
            await client_session.close()

    async def list_job_submissions(self) -> tuple[ErrorResponse | None, JobList | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=self.jobs_endpoint_url,
                headers=self.headers,
                raise_for_status=True,
            ) as response:
                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                return None, JobList(**await response.json())
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

                if err := await self._handle_common_errors_if_necessary(response):
                    return err

                return None
        finally:
            await client_session.close()

    async def register_process_from_cwl_href(
        self,
        cwl_href: str,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.post(
                url=self.processes_endpoint_url,
                headers=self.headers,
                json={"executionUnit": {"href": cwl_href, "type": "application/cwl"}},
            ) as response:
                if response.status == status.HTTP_400_BAD_REQUEST:
                    return ErrorResponse(
                        code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid payload.",
                    ), None
                if response.status == status.HTTP_409_CONFLICT:
                    return (
                        ErrorResponse(
                            code=status.HTTP_409_CONFLICT,
                            detail=f"Process with identical identifier as in '{cwl_href}' already exists.",
                        ),
                        None,
                    )
                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None
                return None, ProcessSummary(**await response.json())
        finally:
            await client_session.close()

    async def register_process_from_local_cwl_file(
        self,
        cwl_location: Path,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.post(
                url=self.processes_endpoint_url,
                headers=self.headers | {"Content-Type": "application/cwl+yaml"},
                data=cwl_location.read_bytes(),
            ) as response:
                if response.status == status.HTTP_400_BAD_REQUEST:
                    return ErrorResponse(
                        code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid payload.",
                    ), None
                if response.status == status.HTTP_409_CONFLICT:
                    return ErrorResponse(
                        code=status.HTTP_409_CONFLICT,
                        detail=f"Process with identical identifier as in '{cwl_location}' already exists.",
                    ), None
                return None, ProcessSummary(**await response.json())
        finally:
            await client_session.close()

    async def process_exists(self, process_identifier: str) -> tuple[ErrorResponse | None, bool | None]:
        err, user_processes = await self.list_processes()
        if err:
            return err, None
        return None, process_identifier in {p.id for p in user_processes.processes}  # type: ignore[union-attr]

    async def ensure_process_exists(self, process_identifier: str) -> ErrorResponse | None:
        if process_identifier not in FUNCTIONS_REGISTRY:
            return ErrorResponse(
                code=status.HTTP_404_NOT_FOUND,
                detail=f"Process '{process_identifier}' does not exist in Action Creator Function Registry. "
                f"Have you made a typo?",
            )

        err, exists = await self.process_exists(process_identifier)
        if err:
            return err
        if exists:
            return None

        cwl_href = FUNCTIONS_REGISTRY[process_identifier]["cwl_href"]
        err, _ = await self.register_process_from_cwl_href(cwl_href=cwl_href)

        return err

    async def list_processes(self) -> tuple[ErrorResponse | None, ProcessList | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=self.processes_endpoint_url,
                headers=self.headers,
                raise_for_status=True,
            ) as response:
                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                return None, ProcessList(**await response.json())
        finally:
            await client_session.close()

    async def get_process_details(self, process_identifier: str) -> tuple[ErrorResponse | None, Process | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.processes_endpoint_url}/{process_identifier}",
                headers=self.headers,
            ) as response:
                if response.status == status.HTTP_404_NOT_FOUND:
                    return ErrorResponse(
                        code=status.HTTP_404_NOT_FOUND,
                        detail=f"Process '{process_identifier}' does not exist.",
                    ), None
                return None, Process(**await response.json())
        finally:
            await client_session.close()

    async def execute_process(
        self,
        process_identifier: str,
        process_inputs: dict[str, Any],
    ) -> tuple[ErrorResponse | None, StatusInfo | None]:
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
                if response.status == status.HTTP_404_NOT_FOUND:
                    return ErrorResponse(
                        code=status.HTTP_404_NOT_FOUND, detail=f"Process '{process_identifier}' does not exist."
                    ), None

                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                return None, StatusInfo(**await response.json())
        finally:
            await client_session.close()

    async def unregister_process(self, process_identifier: str) -> ErrorResponse | None:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.delete(
                url=f"{self.processes_endpoint_url}/{process_identifier}",
                headers=self.headers,
            ) as response:
                if response.status == status.HTTP_403_FORBIDDEN:
                    # ADES returns 403 when unregistering process that does not exist
                    return ErrorResponse(
                        code=status.HTTP_404_NOT_FOUND,
                        detail=f"Process '{process_identifier}' does not exist.",
                    )

                if err := await self._handle_common_errors_if_necessary(response):
                    return err

                return None
        finally:
            await client_session.close()

    async def reregister_process(self, process_identifier: str) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        if process_identifier not in FUNCTIONS_REGISTRY:
            return ErrorResponse(
                code=status.HTTP_404_NOT_FOUND,
                detail=f"Process '{process_identifier}' does not exist in Action Creator Function Registry. "
                f"Have you made a typo?",
            ), None
        if await self.process_exists(process_identifier):
            await self.unregister_process(process_identifier)
        cwl_href = FUNCTIONS_REGISTRY[process_identifier]["cwl_href"]
        return await self.register_process_from_cwl_href(cwl_href)

    @staticmethod
    async def _handle_common_errors_if_necessary(response: ClientResponse) -> ErrorResponse | None:
        if response.status == status.HTTP_400_BAD_REQUEST:
            return ErrorResponse(
                code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload.",
            )

        if response.status == status.HTTP_401_UNAUTHORIZED:
            return ErrorResponse(
                code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to perform this action.",
            )

        if response.status == status.HTTP_429_TOO_MANY_REQUESTS:
            return ErrorResponse(code=status.HTTP_429_TOO_MANY_REQUESTS, detail=(await response.json()).get("detail"))

        if response.status == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return ErrorResponse(code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

        if response.status >= status.HTTP_400_BAD_REQUEST:
            return ErrorResponse(code=response.status, detail=await response.text())

        return None


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
