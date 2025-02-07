from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
from starlette import status

from src.api.v1_2.action_creator.presets import (
    LAND_COVER_CHANGE_DETECTION_PRESET_SPEC,
    NDVI_CLIP_PRESET,
    NDVI_PRESET,
    WATER_QUALITY_PRESET_SPEC,
    WATER_QUALITY_PRESET_SPEC_ARD,
)
from src.services.ades.schemas import StatusCode
from src.services.stac.client import FakeStacClient

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from starlette.testclient import TestClient

_TEST_DATA = [
    {"workflow": p["workflow"]}  # type: ignore[index]
    for p in [
        WATER_QUALITY_PRESET_SPEC,
        WATER_QUALITY_PRESET_SPEC_ARD,
        LAND_COVER_CHANGE_DETECTION_PRESET_SPEC,
        NDVI_CLIP_PRESET,
        NDVI_PRESET,
    ]
]
_TEST_IDS = ["wq", "wq-ard", "lulc", "ndvi-clip-reproject", "simple-ndvi"]


@pytest.mark.parametrize(
    "preset_request_body",
    _TEST_DATA,
    ids=_TEST_IDS,
)
def test_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
    preset_request_body: dict[str, Any],
) -> None:
    # Act
    response = client.post(
        url="/api/v1.2/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=preset_request_body,
    )

    # Assert
    submit_response = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert submit_response["status"] == StatusCode.running.value
    assert submit_response["finished_at"] is None


def test_job_submissions_endpoint_returns_422_when_invalid_stac_collection_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(NDVI_CLIP_PRESET)
    preset_request_body["workflow"]["ndvi"]["inputs"]["stac_collection"] = "dummy-collection"  # type: ignore[index]

    response = client.post(
        url="/api/v1.2/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=preset_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_body = response.json()
    assert response_body["detail"][0]["loc"] == ["body", "workflow", "ndvi", "ndvi", "inputs", "stac_collection"]
    assert response_body["detail"][0]["type"] == "collection_not_supported_error"
    assert response_body["detail"][0]["msg"] == (
        "Collection 'dummy-collection' cannot be used with 'ndvi' function! "
        "Valid options are: ['sentinel-2-l2a', 'sentinel-2-l2a-ard']."
    )


def test_job_submissions_endpoint_returns_422_when_missing_geometry(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(NDVI_CLIP_PRESET)
    preset_request_body["workflow"]["ndvi"]["inputs"].pop("aoi")  # type: ignore[attr-defined]

    # Act
    response = client.post(
        url="/api/v1.2/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=preset_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_body = response.json()
    assert response_body["detail"][0]["loc"] == ["body", "workflow", "ndvi", "ndvi", "inputs", "aoi"]
    assert response_body["detail"][0]["type"] == "missing_area_of_interest_error"
    assert response_body["detail"][0]["msg"] == "Area of Interest is missing."


def test_job_submissions_endpoint_returns_422_when_invalid_date_range_was_provided(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(NDVI_CLIP_PRESET)
    preset_request_body["workflow"]["ndvi"]["inputs"]["date_start"] = "2024-01-01T00:00:00"  # type: ignore[index]
    preset_request_body["workflow"]["ndvi"]["inputs"]["date_end"] = "2023-01-01T00:00:00"  # type: ignore[index]

    # Act
    response = client.post(
        url="/api/v1.2/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=preset_request_body,
    )
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_body = response.json()
    assert response_body["detail"][0]["loc"] == ["body", "workflow", "ndvi", "ndvi", "inputs", "date_end"]
    assert response_body["detail"][0]["type"] == "invalid_date_range_error"
    assert response_body["detail"][0]["msg"] == "End date cannot be before start date."


def test_job_submissions_endpoint_returns_422_when_stac_date_range_is_invalid_ndvi(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(NDVI_CLIP_PRESET)
    preset_request_body["workflow"]["ndvi"]["inputs"]["date_start"] = "2000-01-01T00:00:00"  # type: ignore[index]
    preset_request_body["workflow"]["ndvi"]["inputs"]["date_end"] = "2023-01-01T00:00:00"  # type: ignore[index]

    # Act
    response = client.post(
        url="/api/v1.2/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=preset_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_body = response.json()
    assert response_body["detail"][0]["loc"] == ["body", "workflow", "ndvi", "ndvi", "inputs", "stac_collection"]
    assert response_body["detail"][0]["type"] == "stac_date_range_error"
    assert (
        response_body["detail"][0]["msg"] == "Invalid date range for selected STAC collection: sentinel-2-l2a-ard. "
        "Valid range is between 2015-06-27T10:25:31+00:00 and None."
    )


def test_job_submissions_endpoint_returns_422_when_stac_date_range_is_invalid_lcc(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(LAND_COVER_CHANGE_DETECTION_PRESET_SPEC)
    preset_request_body["workflow"]["land-cover-change-detection"]["inputs"]["date_start"] = "1900-01-01T00:00:00"  # type: ignore[index]
    preset_request_body["workflow"]["land-cover-change-detection"]["inputs"]["date_end"] = "2020-01-01T00:00:00"  # type: ignore[index]

    # Act
    response = client.post(
        url="/api/v1.2/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=preset_request_body,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_body = response.json()
    assert response_body["detail"][0]["loc"] == [
        "body",
        "workflow",
        "land-cover-change-detection",
        "land-cover-change-detection",
        "inputs",
        "stac_collection",
    ]
    assert response_body["detail"][0]["type"] == "stac_date_range_error"
    assert (
        response_body["detail"][0]["msg"] == "Invalid date range for selected STAC collection: esacci-globallc. "
        "Valid range is between 1992-01-01T00:00:00+00:00 and 2015-12-31T23:59:59+00:00."
    )


@patch("src.api.v1_2.action_creator.routes.stac_client_factory")
@pytest.mark.parametrize("wf_spec", _TEST_DATA, ids=_TEST_IDS)
def test_job_submission_endpoint_returns_400_when_no_items_to_process_for_given_workflow_spec(
    stac_client_factory_mock: MagicMock,
    wf_spec: dict[str, Any],
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    stac_client_factory_mock.return_value = FakeStacClient(has_results=False)

    # Act
    response = client.post(
        url="/api/v1.2/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=wf_spec,
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_body = response.json()
    assert (
        response_body["detail"] == "No STAC items found for the selected configuration. "
        "Adjust area, data set, date range, or functions and try again."
    )
