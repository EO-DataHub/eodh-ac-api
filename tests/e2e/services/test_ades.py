from __future__ import annotations

from uuid import uuid4

import pytest
from starlette import status

from src.core.settings import current_settings
from src.services.ades.client import ADESClient, ErrorResponse, ades_client

TEST_PROCESS_IDENTIFIER = "raster-calculate"


@pytest.fixture()
def ades(auth_token: str) -> ADESClient:
    settings = current_settings()
    return ades_client(
        workspace=settings.eodh_auth.username,
        token=auth_token,
    )


# TODO add tests


@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_url(ades: ADESClient) -> None:
    assert ades


@pytest.mark.asyncio(scope="function")
async def test_ades_registering_process_from_file(ades: ADESClient) -> None:
    assert ades


@pytest.mark.asyncio(scope="function")
async def test_ades_listing_process(ades: ADESClient) -> None:
    assert ades


@pytest.mark.asyncio(scope="function")
async def test_ades_executing_job(ades: ADESClient) -> None:
    assert ades


@pytest.mark.asyncio(scope="function")
async def test_ades_listing_job_executions(ades: ADESClient) -> None:
    assert ades


@pytest.mark.asyncio(scope="function")
async def test_ades_getting_job_results(ades: ADESClient) -> None:
    assert ades


@pytest.mark.asyncio(scope="function")
async def test_ades_cancelling_non_existent_job_returns_error_response(ades: ADESClient) -> None:
    result = await ades.cancel_job(uuid4())
    assert isinstance(result, ErrorResponse)
    assert result.code == status.HTTP_404_NOT_FOUND
