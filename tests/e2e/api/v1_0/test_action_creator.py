from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import app as fast_api_app
from src.api.v1_0.action_creator.schemas import ActionCreatorJob, ActionCreatorJobsResponse
from src.services.ades.factory import fake_ades_client_factory
from src.services.ades.fake_client import FakeADESClient
from src.services.ades.schemas import StatusCode
from tests.unit.api.v1_0.schemas.test_functions import TEST_BBOX

if TYPE_CHECKING:
    from fastapi import FastAPI


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return fast_api_app


@pytest.fixture
def mocked_ades_factory() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_0.action_creator.routes.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)


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


def test_get_job_submissions_endpoint_returns_forbidden_error_when_no_token_specified(client: TestClient) -> None:
    # Act
    response = client.get("/api/v1.0/action-creator/submissions")

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_job_submissions_endpoint_returns_unauthorized_error_when_bad_token(client: TestClient) -> None:
    # Act
    response = client.get("/api/v1.0/action-creator/submissions", headers={"Authorization": "Bearer bad_token"})

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    client: TestClient,
    auth_token: str,
) -> None:
    # Act
    response = client.get("/api/v1.0/action-creator/submissions", headers={"Authorization": f"Bearer {auth_token}"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert ActionCreatorJobsResponse(**response.json())


def test_post_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
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
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
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


def test_post_job_submissions_endpoint_returns_422_when_misconfigured_aoi_and_bbox_was_provided(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
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
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
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
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
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
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
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


def test_ws_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Act
    with client.websocket_connect(
        url="/api/v1.0/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json(raster_calculator_request_body)

        # Receive the response for job submission
        submit_response = websocket.receive_json()

        # Assert the initial response (running status)
        assert submit_response["status_code"] == status.HTTP_202_ACCEPTED
        assert submit_response["result"]["status"] == StatusCode.running.value
        assert submit_response["result"]["finished_at"] is None

        # Simulate polling for status update until job is finished
        final_response = websocket.receive_json()

        # Assert final job status
        assert final_response["status_code"] == status.HTTP_200_OK
        assert final_response["result"]["status"] == StatusCode.successful.value
        assert final_response["result"]["finished_at"] is not None


def test_ws_job_submissions_endpoint_returns_422_when_invalid_stac_collection_was_provided(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["stac_collection"] = "dummy-collection"

    with pytest.raises(RuntimeError), client.websocket_connect(  # noqa: PT012
        url="/api/v1.0/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json(raster_calculator_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "collection_not_supported_error"
        assert response["result"]["detail"][0]["msg"] == (
            "Collection 'dummy-collection' cannot be used with 'raster-calculate' function! "
            "Valid options are: ['sentinel-2-l1c', 'sentinel-2-l2a']."
        )
        websocket.close()


def test_ws_job_submissions_endpoint_returns_422_when_misconfigured_aoi_and_bbox_was_provided(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["bbox"] = TEST_BBOX

    # Act
    with pytest.raises(RuntimeError), client.websocket_connect(  # noqa: PT012
        url="/api/v1.0/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json(raster_calculator_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "aoi_bbox_misconfiguration_error"
        assert (
            response["result"]["detail"][0]["msg"] == "AOI and BBOX are mutually exclusive, provide only one of them."
        )


def test_ws_job_submissions_endpoint_returns_422_when_missing_geometry(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"].pop("aoi")

    # Act
    with pytest.raises(RuntimeError), client.websocket_connect(  # noqa: PT012
        url="/api/v1.0/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json(raster_calculator_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "missing_geometry_error"
        assert response["result"]["detail"][0]["msg"] == "At least one of AOI or BBOX must be provided."


def test_ws_job_submissions_endpoint_returns_422_when_invalid_date_range_was_provided(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["date_end"] = "2024-01-01T00:00:00"

    # Act
    with pytest.raises(RuntimeError), client.websocket_connect(  # noqa: PT012
        url="/api/v1.0/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json(raster_calculator_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "invalid_date_range_error"
        assert response["result"]["detail"][0]["msg"] == "End date cannot be before start date."


def test_ws_job_submissions_endpoint_returns_422_when_invalid_bbox_was_provided(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token: str,
    raster_calculator_request_body: dict[str, Any],
) -> None:
    # Arrange
    raster_calculator_request_body["preset_function"]["inputs"]["bbox"] = (1, 1, 10)
    raster_calculator_request_body["preset_function"]["inputs"].pop("aoi")

    # Act
    with pytest.raises(RuntimeError), client.websocket_connect(  # noqa: PT012
        url="/api/v1.0/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json(raster_calculator_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "invalid_bounding_box_error"
        assert (
            response["result"]["detail"][0]["msg"]
            == "BBOX object must be an array of 4 values: [xmin, ymin, xmax, ymax]."
        )
