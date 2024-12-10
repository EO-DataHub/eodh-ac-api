from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from starlette import status

from src.api.v1_0.action_creator.schemas import ActionCreatorJob
from src.consts.action_creator import FUNCTIONS_REGISTRY

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from _pytest.fixtures import FixtureRequest
    from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "request_body_fixture",
    [
        "raster_calculator_request_body",
        "lulc_change_request_body",
        "water_quality_request_body",
    ],
)
def test_post_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
    request_body_fixture: str,
    request: FixtureRequest,
) -> None:
    # Arrange
    request_body = request.getfixturevalue(request_body_fixture)

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert ActionCreatorJob(**response.json())


@pytest.mark.parametrize(
    "request_body_fixture",
    [
        "raster_calculator_request_body",
        "lulc_change_request_body",
        "water_quality_request_body",
    ],
)
def test_post_job_submissions_endpoint_returns_422_when_invalid_stac_collection_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
    request_body_fixture: str,
    request: FixtureRequest,
) -> None:
    # Arrange
    request_body = request.getfixturevalue(request_body_fixture)
    request_body["preset_function"]["inputs"]["stac_collection"] = "dummy-collection"
    func = request_body["preset_function"]["function_identifier"]
    supported_collections = FUNCTIONS_REGISTRY[func]["inputs"]["stac_collection"]["options"]

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function", "stac_collection"]
    assert err["detail"][0]["type"] == "collection_not_supported_error"
    assert err["detail"][0]["msg"] == (
        f"Collection 'dummy-collection' cannot be used with '{func}' function! "
        f"Valid options are: {supported_collections}."
    )


@pytest.mark.parametrize(
    "request_body_fixture",
    [
        "raster_calculator_request_body",
        "lulc_change_request_body",
        "water_quality_request_body",
    ],
)
def test_post_job_submissions_endpoint_returns_422_when_missing_geometry(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
    request_body_fixture: str,
    request: FixtureRequest,
) -> None:
    # Arrange
    request_body = request.getfixturevalue(request_body_fixture)
    request_body["preset_function"]["inputs"].pop("aoi")

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function", "aoi"]
    assert err["detail"][0]["type"] == "missing_area_of_interest_error"
    assert err["detail"][0]["msg"] == "Area of Interest is missing."


@pytest.mark.parametrize(
    "request_body_fixture",
    [
        "raster_calculator_request_body",
        "lulc_change_request_body",
        "water_quality_request_body",
    ],
)
def test_post_job_submissions_endpoint_returns_422_when_invalid_date_range_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
    request_body_fixture: str,
    request: FixtureRequest,
) -> None:
    # Arrange
    request_body = request.getfixturevalue(request_body_fixture)
    request_body["preset_function"]["inputs"]["date_end"] = "2024-01-01T00:00:00"

    # Act
    response = client.post(
        url="/api/v1.0/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    err = response.json()
    assert err["detail"][0]["loc"] == ["body", "preset_function", "date_end"]
    assert err["detail"][0]["type"] == "invalid_date_range_error"
    assert err["detail"][0]["msg"] == "End date cannot be before start date."
