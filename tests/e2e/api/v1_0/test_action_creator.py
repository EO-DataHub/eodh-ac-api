from __future__ import annotations

from typing import Any

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import app
from src.api.v1_0.action_creator.schemas import ActionCreatorJob, ActionCreatorJobsResponse
from tests.unit.api.v1_0.schemas.test_functions import TEST_BBOX

client = TestClient(app)


@pytest.fixture
def raster_calculator_request_body() -> dict[str, Any]:
    return {
        "preset_function": {
            "function_identifier": "raster-calculate",
            "inputs": {
                "aoi": '{"type":"Polygon","coordinates":[[[14.763294437090849,50.833598186651244],'
                "[15.052268923898112,50.833598186651244],[15.052268923898112, 50.989077215056824],"
                "[14.763294437090849, 50.989077215056824],[14.763294437090849, 50.833598186651244]]]}",
                "date_start": "2024-04-03T00:00:00",
                "date_end": "2024-08-01T00:00:00",
                "index": "NDVI",
                "stac_collection": "sentinel-2-l2a",
            },
        }
    }


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
async def test_post_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=raster_calculator_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert ActionCreatorJob(**response.json())


@pytest.mark.asyncio(scope="function")
async def test_post_job_submissions_endpoint_returns_422_when_invalid_stac_collection_was_provided(
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["stac_collection"] = "dummy-collection"

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=raster_calculator_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function"]
    assert err["detail"][0]["type"] == "collection_not_supported_error"
    assert err["detail"][0]["msg"] == (
        "Collection 'dummy-collection' cannot be used with 'raster-calculate' function! "
        "Valid options are: ['sentinel-2-l1c', 'sentinel-2-l2a']."
    )


@pytest.mark.asyncio(scope="function")
async def test_post_job_submissions_endpoint_returns_422_when_misconfigured_aoi_and_bbox_was_provided(
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["bbox"] = TEST_BBOX

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=raster_calculator_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function"]
    assert err["detail"][0]["type"] == "aoi_bbox_misconfiguration_error"
    assert err["detail"][0]["msg"] == "AOI and BBOX are mutually exclusive, provide only one of them."


@pytest.mark.asyncio(scope="function")
async def test_post_job_submissions_endpoint_returns_422_when_missing_geometry(
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"].pop("aoi")

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=raster_calculator_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function"]
    assert err["detail"][0]["type"] == "missing_geometry_error"
    assert err["detail"][0]["msg"] == "At least one of AOI or BBOX must be provided."


@pytest.mark.asyncio(scope="function")
async def test_post_job_submissions_endpoint_returns_422_when_invalid_date_range_was_provided(
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["date_end"] = "2024-01-01T00:00:00"

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=raster_calculator_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function"]
    assert err["detail"][0]["type"] == "invalid_date_range_error"
    assert err["detail"][0]["msg"] == "End date cannot be before start date."


@pytest.mark.asyncio(scope="function")
async def test_post_job_submissions_endpoint_returns_422_when_invalid_bbox_was_provided(
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["bbox"] = (1, 1, 10)
    raster_calculator_request_body["preset_function"]["inputs"].pop("aoi")

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=raster_calculator_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function"]
    assert err["detail"][0]["type"] == "invalid_bounding_box_error"
    assert err["detail"][0]["msg"] == "BBOX object must be an array of 4 values: [xmin, ymin, xmax, ymax]."
