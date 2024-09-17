from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession
from aiohttp_retry import ExponentialRetry, RetryClient
from starlette import status

from src.core.settings import current_settings
from src.utils.logging import get_logger

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID


class ADESService:
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
            raise_for_status=True,
            retry_options=exp_retry,
            logger=self.logger,
        )
        return client_session, retry_client

    async def get_job_details(self, job_id: str | UUID) -> dict[str, Any]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.jobs_endpoint_url}/{job_id}",
                headers=self.headers,
            ) as response:
                return await response.json()  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def get_job_results(self, job_id: str | UUID) -> dict[str, Any]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.jobs_endpoint_url}/{job_id}/results",
                headers=self.headers,
            ) as response:
                return await response.json()  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def list_job_submissions(self) -> dict[str, Any]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=self.jobs_endpoint_url,
                headers=self.headers,
            ) as response:
                return await response.json()  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def submit_job(self, job: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    async def cancel_job(self, job_id: UUID) -> None:
        raise NotImplementedError

    async def register_process(self, process_spec: dict[str, Any]) -> None:
        raise NotImplementedError

    async def list_processes(self) -> dict[str, Any]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=self.processes_endpoint_url,
                headers=self.headers,
            ) as response:
                return await response.json()  # type: ignore[no-any-return]
        finally:
            await client_session.close()

    async def unregister_process(self, process_id: UUID) -> None:
        pass

    async def reregister_process(self, process_spec: dict[str, Any]) -> None:
        pass

    async def get_process_details(self, name: str) -> dict[str, Any]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.get(
                url=f"{self.processes_endpoint_url}/{name}",
                headers=self.headers,
            ) as response:
                return await response.json()  # type: ignore[no-any-return]
        finally:
            await client_session.close()


def ades_service(workspace: str, token: str) -> ADESService:
    settings = current_settings()
    return ADESService(
        url=settings.ades.url,
        ogc_processes_api_path=settings.ades.ogc_processes_api_path,
        ogc_jobs_api_path=settings.ades.ogc_jobs_api_path,
        workspace=workspace,
        logger=get_logger(__name__),
        token=token,
    )
