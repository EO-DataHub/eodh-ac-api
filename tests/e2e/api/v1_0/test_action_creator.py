from __future__ import annotations

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import app
from src.api.v1_0.schemas import ActionCreatorJob, ActionCreatorJobsResponse

client = TestClient(app)


@pytest.mark.asyncio(scope="function")
async def test_get_job_submissions_endpoint_returns_forbidden_error_when_no_token_specified() -> None:
    # Act
    response = client.get("/api/v1.0/action-creator/submissions")

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio(scope="function")
async def test_get_job_submissions_endpoint_returns_unauthorized_error_when_bad_token() -> None:
    # Act
    response = client.get("/api/v1.0/action-creator/submissions", headers={"Authorization": "Bearer bad_token"})

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(scope="function")
async def test_get_job_submissions_endpoint_returns_valid_response_when_all_is_ok(auth_token: str) -> None:
    # Act
    response = client.get("/api/v1.0/action-creator/submissions", headers={"Authorization": f"Bearer {auth_token}"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert ActionCreatorJobsResponse(**response.json())


@pytest.mark.asyncio(scope="function")
async def test_post_job_submissions_endpoint_returns_valid_response_when_all_is_ok(auth_token: str) -> None:
    # Arrange
    request_body = {
        "preset_function": {
            "function_identifier": "raster-calculate",
            "inputs": {
                "aoi": '{"type":"Polygon","coordinates":[[[14.763294437090849,50.833598186651244],'
                "[15.052268923898112,50.833598186651244],[15.052268923898112, 50.989077215056824],"
                "[14.763294437090849, 50.989077215056824],[14.763294437090849, 50.833598186651244]]]}",
                "date_end": "2024-08-01T00:00:00",
                "date_start": "2024-04-03T00:00:00",
                "index": "NDVI",
                "stac_collection": "sentinel-2-l2a",
            },
        }
    }

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert ActionCreatorJob(**response.json())
