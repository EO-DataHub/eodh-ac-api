from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID

    from src.services.ades.schemas import JobList, Process, ProcessList, ProcessSummary, StatusInfo


class ErrorResponse(BaseModel):
    code: int
    detail: str | dict[str, Any] | None = None


class ADESClientBase(abc.ABC):
    @abc.abstractmethod
    async def get_job_details(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]: ...

    @abc.abstractmethod
    async def get_job_results(self, job_id: str | UUID) -> tuple[ErrorResponse | None, dict[str, Any] | None]: ...

    @abc.abstractmethod
    async def list_job_submissions(
        self,
        *,
        raw_output: bool = False,
    ) -> tuple[ErrorResponse | None, JobList | dict[str, Any] | None]: ...

    @abc.abstractmethod
    async def cancel_job(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]: ...

    @abc.abstractmethod
    async def register_process_from_local_cwl_file(
        self,
        cwl_location: Path,
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
