from __future__ import annotations

import json
import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import aiohttp
import yaml
from dotenv import load_dotenv
from starlette import status

from src import consts
from src.services.ades.base_client import ADESClientBase, ErrorResponse
from src.services.ades.schemas import JobList, Process, ProcessList, ProcessSummary, StatusInfo
from src.utils.logging import get_logger

if TYPE_CHECKING:
    import datetime
    from logging import Logger
    from uuid import UUID


_logger = get_logger(__name__)


def replace_placeholders_in_text(content: str) -> str:
    load_dotenv(consts.directories.ROOT_DIR / ".env")
    pattern = re.compile(r"<<([A-Za-z\-_ ]+)>>")
    placeholders = re.findall(pattern=pattern, string=content)

    for placeholder in placeholders:
        replacement = os.environ.get(placeholder.strip(), '""')
        content = content.replace(f"<<{placeholder}>>", replacement)

    return content


def replace_placeholders_in_cwl_file(file_path: Path) -> None:
    content = file_path.read_text(encoding="utf-8")
    content = replace_placeholders_in_text(content)

    file_path.write_text(content, encoding="utf-8")


def override_id_in_cwl_if_necessary(file_path: Path, id_override: str | None) -> bytes:
    if id_override is not None:
        data = yaml.safe_load(file_path.open(encoding="utf-8"))
        for obj in data["$graph"]:
            if obj["class"] == "Workflow":
                obj["id"] = id_override
                break
        file_path.write_text(yaml.dump(data), encoding="utf-8")

    return file_path.read_bytes()


class ADESClient(ADESClientBase):
    def __init__(
        self,
        url: str,
        ogc_processes_api_path: str,
        ogc_jobs_api_path: str,
        workspace: str,
        token: str,
        logger: Logger,
    ) -> None:
        super().__init__(url, logger)
        self.ogc_jobs_api_path = ogc_jobs_api_path
        self.ogc_processes_api_path = ogc_processes_api_path
        self.token = token
        self.workspace = workspace
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

    async def _download_file(self, file_url: str, output_path: Path) -> tuple[ErrorResponse | None, Path | None]:
        client_session, retry_client = self._get_retry_client()

        try:
            async with retry_client.get(file_url) as response:
                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None
                parsed = urlparse(file_url)
                fname = parsed.path.split("/")[-1]
                fp = output_path / fname
                fp.write_bytes(await response.content.read())
                return None, fp
        finally:
            await client_session.close()

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

    async def list_job_submissions(
        self,
        *,
        limit: int = 100,
        skip: int = 0,
        raw_output: bool = False,
    ) -> tuple[ErrorResponse | None, JobList | dict[str, Any] | None]:
        client_session, retry_client = self._get_retry_client(max_timeout=120)
        try:
            async with retry_client.get(
                url=f"{self.jobs_endpoint_url}?limit={limit}&skip={skip}",
                headers=self.headers,
                raise_for_status=True,
            ) as response:
                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                if raw_output:
                    return None, await response.json()

                return None, JobList(**await response.json())
        finally:
            await client_session.close()

    async def cancel_or_delete_job(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.delete(
                url=f"{self.jobs_endpoint_url}/{job_id}",
                headers=self.headers,
            ) as response:
                # ADES returns 403 when cancelling non-existent job
                if response.status == status.HTTP_403_FORBIDDEN:
                    return ErrorResponse(code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' does not exist."), None

                if response.status == status.HTTP_501_NOT_IMPLEMENTED:
                    return ErrorResponse(
                        code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail="Job cancellation is not implemented.",
                    ), None

                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                return None, StatusInfo(**json.loads(await response.text()))
        finally:
            await client_session.close()

    async def register_process_from_cwl_href_with_download(
        self,
        cwl_href: str,
        id_override: str | None = None,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        with TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            err, fp = await self._download_file(file_url=cwl_href, output_path=tmp_dir_path)
            if err:
                return err, None
            if fp is None:
                return ErrorResponse(code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error."), None
            replace_placeholders_in_cwl_file(fp)
            return await self.register_process_from_local_cwl_file(fp, id_override)

    async def register_process_from_local_cwl_file(
        self,
        cwl_location: Path,
        id_override: str | None = None,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            data = override_id_in_cwl_if_necessary(cwl_location, id_override)
            async with retry_client.post(
                url=self.processes_endpoint_url,
                headers=self.headers | {"Content-Type": "application/cwl+yaml"},
                data=data,
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

    async def ensure_process_exists(
        self,
        process_identifier: str,
        wf_registry: dict[str, dict[str, str]],
    ) -> ErrorResponse | None:
        if process_identifier not in wf_registry:
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

        cwl_href = wf_registry[process_identifier]["cwl_href"]
        err, _ = await self.register_process_from_cwl_href_with_download(cwl_href=cwl_href)

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

            _logger.info("Executing process: %s with inputs: %s", process_identifier, json.dumps(process_inputs))

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

    async def reregister_process(
        self,
        process_identifier: str,
        wf_registry: dict[str, dict[str, str]],
        wf_id_override_lookup: dict[str, str],
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        if process_identifier not in wf_registry:
            return ErrorResponse(
                code=status.HTTP_404_NOT_FOUND,
                detail=f"Process '{process_identifier}' does not exist in Action Creator Function Registry. "
                f"Have you made a typo?",
            ), None
        if await self.process_exists(process_identifier):
            _ = await self.unregister_process(process_identifier)
        cwl_href = wf_registry[process_identifier]["cwl_href"]
        id_override = wf_id_override_lookup.get(process_identifier)
        return await self.register_process_from_cwl_href_with_download(cwl_href, id_override=id_override)

    async def batch_cancel_or_delete_jobs(  # noqa: C901
        self,
        *,
        stac_endpoint: str,
        remove_statuses: list[str] | None,
        remove_all_before: datetime.datetime | None = None,
        remove_all_after: datetime.datetime | None = None,
        max_jobs_to_process: int = 1000,
        remove_jobs_without_results: bool = False,
    ) -> tuple[ErrorResponse | None, list[str] | None]:
        if remove_statuses is None:
            remove_statuses = []

        removed_ids = []

        async def delete_job(job: dict[str, Any]) -> ErrorResponse | None:
            err, _ = await self.cancel_or_delete_job(job["jobID"])
            removed_ids.append(job["jobID"])
            return err

        jobs: dict[str, Any] | None
        err, jobs = await self.list_job_submissions(raw_output=True, limit=max_jobs_to_process)
        if err:
            return err, None

        assert jobs is not None  # noqa: S101

        for job in jobs["jobs"]:
            _logger.info("Running batch delete for job history, processing job: %s", job["jobID"])

            if job["status"] in remove_statuses:
                _logger.info("Removing job: %s with status: %s", job["jobID"], job["status"])
                err = await delete_job(job)
                if err:
                    return err, None
                continue

            if remove_all_after and job["created"] > remove_all_after.isoformat():
                _logger.info(
                    "Removing job submission %s, because it is after cutoff date: %s", job["jobID"], job["created"]
                )
                err = await delete_job(job)
                if err:
                    return err, None
                continue

            if remove_all_before and job["created"] < remove_all_before.isoformat():
                _logger.info(
                    "Removing job submission %s, because it is before cutoff date: %s", job["jobID"], job["created"]
                )
                err = await delete_job(job)
                if err:
                    return err, None
                continue

            if job["status"] == "successful" and remove_jobs_without_results:
                async with (
                    aiohttp.ClientSession() as session,
                    session.post(
                        f"{stac_endpoint}/catalogs/user/catalogs/{self.workspace}/catalogs/processing-results/catalogs/{job['processID']}/catalogs/cat_{job['jobID']}/search",
                        headers={
                            "Authorization": f"Bearer {self.token}",
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        },
                        json={
                            "limit": 1,
                            "sortby": [{"field": "properties.datetime", "direction": "desc"}],
                            "filter-lang": "cql-json",
                            "fields": {},
                        },
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response,
                ):
                    if response.status == status.HTTP_200_OK:
                        continue
                    _logger.info(
                        "Removing job: %s - EODH STAC API returned: %s - job has no results.",
                        job["jobID"],
                        response.status,
                    )
                    err = await delete_job(job)
                    if err:
                        return err, None

        return None, removed_ids
