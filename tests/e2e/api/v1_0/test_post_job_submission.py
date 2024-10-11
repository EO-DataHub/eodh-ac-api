from __future__ import annotations

from typing import TYPE_CHECKING, Any

from starlette import status

from src.api.v1_0.action_creator.schemas import ActionCreatorJob
from tests.unit.api.v1_0.schemas.test_functions import TEST_BBOX

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from starlette.testclient import TestClient


def test_post_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
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


def test_post_job_submissions_endpoint_returns_422_when_invalid_stac_collection_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
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
        "Valid options are: ['sentinel-2-l2a']."
    )


def test_post_job_submissions_endpoint_returns_422_when_misconfigured_aoi_and_bbox_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
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


def test_post_job_submissions_endpoint_returns_422_when_missing_geometry(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
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


def test_post_job_submissions_endpoint_returns_422_when_invalid_date_range_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
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


def test_post_job_submissions_endpoint_returns_422_when_invalid_bbox_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
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
