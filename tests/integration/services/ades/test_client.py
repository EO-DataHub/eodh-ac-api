from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from aiohttp import ClientSession
from starlette import status

from src.core.settings import current_settings
from src.services.ades.client import ADESClient, ades_client
from src.services.ades.schemas import StatusCode

if TYPE_CHECKING:
    from pathlib import Path

TEST_PROCESS_IDENTIFIER = "water_bodies"
RASTER_CALCULATOR_PROCESS_IDENTIFIER = "raster-calculate"
TEST_WATER_BODIES_CWL_HREF = "https://raw.githubusercontent.com/Terradue/ogc-eo-application-package-hands-on/refs/heads/master/water-bodies/app-package.cwl"
TEST_PROCESS_INPUTS = {
    "stac_items": [
        "https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l2a-cogs/items/S2B_10TFK_20210713_0_L2A",
        "https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l2a-cogs/items/S2A_10TFK_20220524_0_L2A",
    ],
    "aoi": "-121.399,39.834,-120.74,40.472",
    "epsg": "EPSG:4326",
}
NON_EXISTENT_PROCESS_ID = NON_EXISTENT_JOB_ID = "i-dont-exist"


@pytest.fixture
def ades(auth_token: str) -> ADESClient:
    settings = current_settings()
    return ades_client(
        workspace=settings.eodh_auth.username,
        token=auth_token,
    )


async def get_cwl_from_href(cwl_href: str, save_dir: Path) -> Path:
    async with ClientSession() as session:
        response = await session.get(cwl_href)

    fp = save_dir / "app.cwl"
    fp.write_bytes(await response.content.read())
    return fp


@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_url(ades: ADESClient) -> None:
    # Arrange - ensure process not registered
    err = await ades.unregister_process(TEST_PROCESS_IDENTIFIER)
    assert err is None or err.code == status.HTTP_404_NOT_FOUND

    # Act
    err, result = await ades.register_process_from_cwl_href(TEST_WATER_BODIES_CWL_HREF)

    # Assert
    assert err is None
    assert result is not None
    assert result.id == TEST_PROCESS_IDENTIFIER


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


@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_twice_results_in_conflict(ades: ADESClient) -> None:
    # Arrange - ensure process registered
    err, _ = await ades.register_process_from_cwl_href(TEST_WATER_BODIES_CWL_HREF)
    assert err is None or err.code == status.HTTP_409_CONFLICT

    # Act - register 2nd time
    err, _ = await ades.register_process_from_cwl_href(TEST_WATER_BODIES_CWL_HREF)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_file(ades: ADESClient, tmp_path: Path) -> None:
    # Arrange - ensure process not registered
    err = await ades.unregister_process(TEST_PROCESS_IDENTIFIER)
    assert err is None or err.code == status.HTTP_404_NOT_FOUND

    # Get the CWL file content
    tmp_file = await get_cwl_from_href(cwl_href=TEST_WATER_BODIES_CWL_HREF, save_dir=tmp_path)

    # Act
    err, result = await ades.register_process_from_local_cwl_file(tmp_file)

    # Assert
    assert err is None
    assert result is not None
    assert result.id == TEST_PROCESS_IDENTIFIER
    assert await ades.process_exists(TEST_PROCESS_IDENTIFIER)


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


@pytest.mark.asyncio(scope="function")
async def test_ades_reregistering_process_with_unknown_function_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.reregister_process(NON_EXISTENT_PROCESS_ID)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert result is None
    assert err.detail == (
        f"Process '{NON_EXISTENT_PROCESS_ID}' does not exist in Action Creator Function Registry. "
        f"Have you made a typo?"
    )


@pytest.mark.asyncio(scope="function")
async def test_ades_unregister_non_existent_process_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err = await ades.unregister_process(NON_EXISTENT_PROCESS_ID)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert err.detail == f"Process '{NON_EXISTENT_PROCESS_ID}' does not exist."


@pytest.mark.asyncio(scope="function")
async def test_ades_listing_process(ades: ADESClient) -> None:
    # Act
    err, response = await ades.list_processes()

    # Assert
    assert err is None
    assert response is not None
    assert response.processes


@pytest.mark.asyncio(scope="function")
async def test_ades_get_process_details(ades: ADESClient) -> None:
    # Act
    err, result = await ades.get_process_details(TEST_PROCESS_IDENTIFIER)

    # Assert
    assert err is None
    assert result is not None
    assert result.id == TEST_PROCESS_IDENTIFIER


@pytest.mark.asyncio(scope="function")
async def test_ades_get_non_existent_process_details_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.get_process_details(NON_EXISTENT_PROCESS_ID)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert err.detail == f"Process '{NON_EXISTENT_PROCESS_ID}' does not exist."
    assert result is None


@pytest.mark.asyncio(scope="function")
async def test_ades_executing_job(ades: ADESClient) -> None:
    # Arrange - ensure process registered
    err, _ = await ades.register_process_from_cwl_href(TEST_WATER_BODIES_CWL_HREF)
    assert err is None or err.code == status.HTTP_409_CONFLICT

    # Act
    # Execute the process
    err, execution_result = await ades.execute_process(
        process_identifier=TEST_PROCESS_IDENTIFIER,
        process_inputs=TEST_PROCESS_INPUTS,
    )
    assert err is None
    assert execution_result is not None

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
    assert execution_result is not None
    assert execution_result.process_id == TEST_PROCESS_IDENTIFIER
    assert execution_result.job_id
    assert execution_result.status == StatusCode.running
    assert status_result.status in {StatusCode.failed, StatusCode.successful}


@pytest.mark.asyncio(scope="function")
async def test_ades_listing_job_executions(ades: ADESClient) -> None:
    # Arrange
    err, _ = await ades.execute_process(
        process_identifier=TEST_PROCESS_IDENTIFIER,
        process_inputs=TEST_PROCESS_INPUTS,
    )
    assert err is None

    # Act
    err, result = await ades.list_job_submissions()

    # Assert
    assert err is None
    assert result is not None
    assert result.jobs
    assert result.number_total > 0


@pytest.mark.asyncio(scope="function")
async def test_ades_get_non_existent_job_details_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.get_job_results(NON_EXISTENT_JOB_ID)

    # Assert
    assert err is not None
    assert result is None
    assert err.code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(scope="function")
async def test_ades_getting_job_results(ades: ADESClient, tmp_path: Path) -> None:
    # Arrange
    # Ensure process not registered
    err = await ades.unregister_process(TEST_PROCESS_IDENTIFIER)
    assert err is None or err.code == status.HTTP_404_NOT_FOUND
    tmp_file = await get_cwl_from_href(cwl_href=TEST_WATER_BODIES_CWL_HREF, save_dir=tmp_path)
    err, _ = await ades.register_process_from_local_cwl_file(tmp_file)
    assert err is None

    # Execute the process
    err, execution_result = await ades.execute_process(
        process_identifier=TEST_PROCESS_IDENTIFIER,
        process_inputs=TEST_PROCESS_INPUTS,
    )
    assert err is None
    assert execution_result is not None

    # Poll for changes while process is running
    while True:
        err, response = await ades.get_job_details(execution_result.job_id)
        assert err is None
        assert response is not None
        if response.status != StatusCode.running:
            break
        await asyncio.sleep(5)

    # Act
    err, job_results = await ades.get_job_results(execution_result.job_id)

    # Assert
    assert err is None
    assert job_results


@pytest.mark.asyncio(scope="function")
async def test_ades_getting_non_existent_job_results_of_returns_404_not_found(ades: ADESClient) -> None:
    # Act
    err, result = await ades.get_job_results(NON_EXISTENT_JOB_ID)

    # Assert
    assert err is not None
    assert result is None
    assert err.code == status.HTTP_404_NOT_FOUND
    assert err.detail == f"Job '{NON_EXISTENT_JOB_ID}' does not exist."


@pytest.mark.asyncio(scope="function")
async def test_ades_cancelling_job_returns_501_not_implemented(ades: ADESClient) -> None:
    # Arrange
    # Execute the process
    err, execution_result = await ades.execute_process(
        process_identifier=TEST_PROCESS_IDENTIFIER,
        process_inputs=TEST_PROCESS_INPUTS,
    )
    assert err is None
    assert execution_result is not None

    # Act
    err = await ades.cancel_job(execution_result.job_id)

    # Assert
    assert err is not None
    assert err.code == status.HTTP_501_NOT_IMPLEMENTED


@pytest.mark.asyncio(scope="function")
async def test_ades_cancelling_non_existent_job_returns_error_response(ades: ADESClient) -> None:
    # Act
    result = await ades.cancel_job(uuid4())

    # Assert
    assert result is not None
    assert result.code == status.HTTP_404_NOT_FOUND
