from __future__ import annotations

from uuid import uuid4

import pytest

from src import consts
from src.core.settings import current_settings
from src.services.ades.client import ADESClient, ades_client

TEST_PROCESS_IDENTIFIER = "raster-calculate"


@pytest.fixture()
def ades(auth_token: str) -> ADESClient:
    settings = current_settings()
    return ades_client(
        workspace=settings.eodh_auth.username,
        token=auth_token,
    )


@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_url(ades: ADESClient) -> None:
    # Arrange
    # Make sure we don't have this process registered
    processes = await ades.list_processes()
    if [p for p in processes["processes"] if p["id"] == TEST_PROCESS_IDENTIFIER]:
        # Unregister the process if it exists
        await ades.unregister_process(process_identifier=TEST_PROCESS_IDENTIFIER)

    # Act
    func_to_run = next(iter(f for f in consts.action_creator.FUNCTIONS if f["name"] == TEST_PROCESS_IDENTIFIER))
    result = await ades.register_process_from_cwl_href(cwl_href=func_to_run["cwl_href"])  # type: ignore[arg-type]

    # Assert
    assert all(k in result for k in ("processes", "links"))


@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_file(ades: ADESClient) -> None:
    assert ades
    raise NotImplementedError


@pytest.mark.asyncio(scope="function")
async def test_ades_listing_process(ades: ADESClient) -> None:
    assert ades
    raise NotImplementedError


@pytest.mark.asyncio(scope="function")
async def test_ades_executing_job(ades: ADESClient) -> None:
    assert ades
    raise NotImplementedError


@pytest.mark.asyncio(scope="function")
async def test_ades_listing_job_executions(ades: ADESClient) -> None:
    assert ades
    raise NotImplementedError


@pytest.mark.asyncio(scope="function")
async def test_ades_getting_job_results(ades: ADESClient) -> None:
    assert ades
    raise NotImplementedError


@pytest.mark.asyncio(scope="function")
async def test_ades_cancelling_submitted_job(ades: ADESClient) -> None:
    with pytest.raises(NotImplementedError):
        await ades.cancel_job(uuid4())
