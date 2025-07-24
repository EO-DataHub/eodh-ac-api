from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from aiohttp import ClientSession
from flaky import flaky
from starlette import status

from src.core.settings import current_settings
from src.services.ades.factory import ades_client_factory
from src.services.ades.schemas import JobList, StatusCode

if TYPE_CHECKING:
    from pathlib import Path

    from src.services.ades.client import ADESClient

from src.consts.geometries import INDIAN_OCEAN_AOI

RASTER_CALCULATOR_PROCESS_IDENTIFIER = "raster-calculate"
RASTER_CALCULATOR_CWL_HREF = (
    "https://raw.githubusercontent.com/EO-DataHub/eodh-workflows/main/cwl_files/raster-calculate-app.cwl"
)
RASTER_CALCULATOR_INPUTS = {
    "aoi": json.dumps(INDIAN_OCEAN_AOI),
    "date_start": "2024-01-01T00:00:00",
    "date_end": "2024-08-01T00:00:00",
    "index": "NDVI",
    "stac_collection": "sentinel-2-l2a",
    "limit": 1,
    "clip": "True",
}
NON_EXISTENT_PROCESS_ID = NON_EXISTENT_JOB_ID = "i-dont-exist"


@pytest.fixture
def ades(ws_token: str) -> ADESClient:
    settings = current_settings()
    return ades_client_factory(
        workspace=settings.eodh.username,
        token=ws_token,
    )


async def get_cwl_from_href(cwl_href: str, save_dir: Path) -> Path:
    async with ClientSession() as session:
        response = await session.get(cwl_href)

    fp = save_dir / "app.cwl"
    fp.write_bytes(await response.content.read())
    return fp


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_url_with_download(ades: ADESClient) -> None:
    # Arrange - ensure process not registered
    err = await ades.unregister_process(RASTER_CALCULATOR_PROCESS_IDENTIFIER)
    assert err is None or err.code == status.HTTP_404_NOT_FOUND

    # Act
    err, result = await ades.register_process_from_cwl_href_with_download(RASTER_CALCULATOR_CWL_HREF)

    # Assert
    assert err is None
    assert result is not None
    assert result.id == RASTER_CALCULATOR_PROCESS_IDENTIFIER


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_ensure_process_exists(ades: ADESClient) -> None:
    # Arrange - ensure process not registered
    err = await ades.unregister_process(RASTER_CALCULATOR_PROCESS_IDENTIFIER)
    assert err is None or err.code == status.HTTP_404_NOT_FOUND

    # Act
    err = await ades.ensure_process_exists(RASTER_CALCULATOR_PROCESS_IDENTIFIER)

    # Assert
    assert err is None
    assert await ades.process_exists(RASTER_CALCULATOR_PROCESS_IDENTIFIER)
    err, processes = await ades.list_processes()
    assert err is None
    assert processes is not None
    assert any(p for p in processes.processes if p.id == RASTER_CALCULATOR_PROCESS_IDENTIFIER)


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_twice_results_in_conflict(ades: ADESClient) -> None:
    # Arrange - ensure process registered
    err, _ = await ades.register_process_from_cwl_href_with_download(RASTER_CALCULATOR_CWL_HREF)
    assert err is None or err.code == status.HTTP_409_CONFLICT

    # Act - register 2nd time
    err, _ = await ades.register_process_from_cwl_href_with_download(RASTER_CALCULATOR_CWL_HREF)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_409_CONFLICT


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_file(ades: ADESClient, tmp_path: Path) -> None:
    # Arrange - ensure process not registered
    err = await ades.unregister_process(RASTER_CALCULATOR_PROCESS_IDENTIFIER)
    assert err is None or err.code == status.HTTP_404_NOT_FOUND

    # Get the CWL file content
    tmp_file = await get_cwl_from_href(cwl_href=RASTER_CALCULATOR_CWL_HREF, save_dir=tmp_path)

    # Act
    err, result = await ades.register_process_from_local_cwl_file(tmp_file)

    # Assert
    assert err is None
    assert result is not None
    assert result.id == RASTER_CALCULATOR_PROCESS_IDENTIFIER
    assert await ades.process_exists(RASTER_CALCULATOR_PROCESS_IDENTIFIER)


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_reregistering_process(ades: ADESClient) -> None:
    # Arrange - ensure process not registered
    err = await ades.unregister_process(RASTER_CALCULATOR_PROCESS_IDENTIFIER)
    assert err is None or err.code == status.HTTP_404_NOT_FOUND

    # Act
    err, result = await ades.reregister_process(RASTER_CALCULATOR_PROCESS_IDENTIFIER)

    # Assert
    assert err is None
    assert result is not None
    assert result.id == RASTER_CALCULATOR_PROCESS_IDENTIFIER
    assert await ades.process_exists(RASTER_CALCULATOR_PROCESS_IDENTIFIER)


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_reregistering_process_with_unknown_function_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.reregister_process(NON_EXISTENT_PROCESS_ID)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert result is None
    assert err.detail == (
        f"Process '{NON_EXISTENT_PROCESS_ID}' does not exist in Action Creator Function Registry. Have you made a typo?"
    )


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_unregister_non_existent_process_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err = await ades.unregister_process(NON_EXISTENT_PROCESS_ID)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert err.detail == json.dumps({
        "title": "NoSuchProcess",
        "type": "http://www.opengis.net/def/rel/ogc/1.0/exception/no-such-process",
        "detail": "Unable to parse the ZCFG file: i-dont-exist.zcfg (No message provided)",
    })


@pytest.mark.asyncio(scope="function")
async def test_ades_listing_process(ades: ADESClient) -> None:
    # Act
    err, response = await ades.list_processes()

    # Assert
    assert err is None
    assert response is not None
    assert response.processes


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_get_process_details(ades: ADESClient) -> None:
    # Arrange
    err, _ = await ades.register_process_from_cwl_href_with_download(RASTER_CALCULATOR_CWL_HREF)
    assert err is None or err.code == status.HTTP_409_CONFLICT

    # Act
    err, result = await ades.get_process_details(RASTER_CALCULATOR_PROCESS_IDENTIFIER)

    # Assert
    assert err is None
    assert result is not None
    assert result.id == RASTER_CALCULATOR_PROCESS_IDENTIFIER
    assert result.inputs is not None
    assert all(k in result.inputs for k in ("stac_collection", "date_start", "date_end", "aoi"))


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_get_non_existent_process_details_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.get_process_details(NON_EXISTENT_PROCESS_ID)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert err.detail == f"Process '{NON_EXISTENT_PROCESS_ID}' does not exist."
    assert result is None


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_executing_job(ades: ADESClient) -> None:
    # Arrange - ensure process registered
    err, _ = await ades.register_process_from_cwl_href_with_download(RASTER_CALCULATOR_CWL_HREF)
    assert err is None or err.code == status.HTTP_409_CONFLICT

    # Act #1
    # Execute the process
    err, execution_result = await ades.execute_process(
        process_identifier=RASTER_CALCULATOR_PROCESS_IDENTIFIER,
        process_inputs=RASTER_CALCULATOR_INPUTS,
    )
    assert err is None
    assert execution_result is not None
    assert execution_result is not None
    assert execution_result.process_id == RASTER_CALCULATOR_PROCESS_IDENTIFIER
    assert execution_result.job_id
    assert execution_result.status == StatusCode.running

    # Poll for changes while process is running
    while True:
        err, status_result = await ades.get_job_details(execution_result.job_id)
        assert err is None
        assert status_result is not None
        if status_result.status != StatusCode.running:
            break
        await asyncio.sleep(5)

    # Assert
    assert err is None
    assert status_result.status in {StatusCode.failed, StatusCode.successful}
    assert status_result.finished is not None

    # Act #2
    # List job submissions
    list_jobs_result: JobList
    err, list_jobs_result = await ades.list_job_submissions()  # type: ignore[assignment]

    # Assert
    assert err is None
    assert list_jobs_result is not None
    assert list_jobs_result.jobs
    assert list_jobs_result.number_total > 0

    # Act #3
    # List job results
    err, _ = await ades.get_job_results(execution_result.job_id)

    # Assert
    assert err is None

    # Cleanup afterward
    await ades.cancel_or_delete_job(execution_result.job_id)


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_get_non_existent_job_details_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.get_job_results(NON_EXISTENT_JOB_ID)

    # Assert
    assert err is not None
    assert result is None
    assert err.code == status.HTTP_404_NOT_FOUND


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_getting_non_existent_job_results_of_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.get_job_results(NON_EXISTENT_JOB_ID)

    # Assert
    assert err is not None
    assert result is None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert err.detail == f"Job '{NON_EXISTENT_JOB_ID}' does not exist."


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_cancelling_job_returns_204(ades: ADESClient) -> None:
    # Arrange
    # Execute the process
    err, execution_result = await ades.execute_process(
        process_identifier=RASTER_CALCULATOR_PROCESS_IDENTIFIER,
        process_inputs=RASTER_CALCULATOR_INPUTS,
    )
    assert err is None
    assert execution_result is not None

    # Act
    err, result = await ades.cancel_or_delete_job(execution_result.job_id)

    # Assert
    assert err is None
    assert result is not None
    assert result.status == "dismissed"


@flaky(max_runs=3)
@pytest.mark.asyncio(scope="function")
async def test_ades_cancelling_non_existent_job_returns_error_response(ades: ADESClient) -> None:
    # Act
    err, result = await ades.cancel_or_delete_job(uuid4())

    # Assert
    assert result is None
    assert err is not None
    assert err.code == status.HTTP_404_NOT_FOUND
