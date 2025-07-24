from __future__ import annotations

import abc
import dataclasses
from typing import TYPE_CHECKING, Any

from aiohttp import ClientResponse, ClientSession
from aiohttp_retry import ExponentialRetry, RetryClient
from pydantic import BaseModel
from starlette import status

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path
    from uuid import UUID

    from src.services.ades.schemas import JobList, Process, ProcessList, ProcessSummary, StatusInfo


class ErrorResponse(BaseModel):
    code: int
    detail: str | dict[str, Any] | None = None


@dataclasses.dataclass
class APIClient:
    url: str
    logger: Logger

    def _get_retry_client(
        self,
        attempts: int = 3,
        max_timeout: float = 10,
        start_timeout: float = 2,
    ) -> tuple[ClientSession, RetryClient]:
        client_session = ClientSession()
        exp_retry = ExponentialRetry(
            attempts=attempts,
            max_timeout=max_timeout,
            statuses={
                status.HTTP_429_TOO_MANY_REQUESTS,
                status.HTTP_502_BAD_GATEWAY,
                status.HTTP_503_SERVICE_UNAVAILABLE,
            },
            start_timeout=start_timeout,
        )
        retry_client = RetryClient(
            client_session=client_session,
            retry_options=exp_retry,
            logger=self.logger,
        )
        return client_session, retry_client

    async def _handle_common_errors_if_necessary(self, response: ClientResponse) -> ErrorResponse | None:
        if response.status >= status.HTTP_400_BAD_REQUEST:
            self.logger.warning(
                "Response for %s %s, does not indicate success. Status code: %s",
                response.method,
                response.url,
                response.status,
            )

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


class ADESClientBase(APIClient, abc.ABC):
    @abc.abstractmethod
    async def get_job_details(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]: ...

    @abc.abstractmethod
    async def get_job_results(self, job_id: str | UUID) -> tuple[ErrorResponse | None, dict[str, Any] | None]: ...

    @abc.abstractmethod
    async def list_job_submissions(
        self,
        *,
        limit: int = 100,
        skip: int = 0,
        raw_output: bool = False,
    ) -> tuple[ErrorResponse | None, JobList | dict[str, Any] | None]: ...

    @abc.abstractmethod
    async def cancel_or_delete_job(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]: ...

    @abc.abstractmethod
    async def register_process_from_cwl_href_with_download(
        self,
        cwl_href: str,
        id_override: str | None = None,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]: ...

    @abc.abstractmethod
    async def register_process_from_local_cwl_file(
        self,
        cwl_location: Path,
        id_override: str | None = None,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]: ...

    @abc.abstractmethod
    async def process_exists(self, process_identifier: str) -> tuple[ErrorResponse | None, bool | None]: ...

    @abc.abstractmethod
    async def ensure_process_exists(self, process_identifier: str) -> ErrorResponse | None: ...

    @abc.abstractmethod
    async def list_processes(self) -> tuple[ErrorResponse | None, ProcessList | None]: ...

    @abc.abstractmethod
    async def get_process_details(self, process_identifier: str) -> tuple[ErrorResponse | None, Process | None]: ...

    @abc.abstractmethod
    async def execute_process(
        self,
        process_identifier: str,
        process_inputs: dict[str, Any],
    ) -> tuple[ErrorResponse | None, StatusInfo | None]: ...

    @abc.abstractmethod
    async def unregister_process(self, process_identifier: str) -> ErrorResponse | None: ...

    @abc.abstractmethod
    async def reregister_process(
        self, process_identifier: str
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]: ...
