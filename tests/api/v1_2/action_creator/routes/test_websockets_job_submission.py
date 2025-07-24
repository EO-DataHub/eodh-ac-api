from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

import pytest
from starlette import status

from src.api.v1_2.action_creator.presets import LAND_COVER_CHANGE_DETECTION_PRESET_SPEC, NDVI_CLIP_PRESET, NDVI_PRESET
from src.services.ades.schemas import StatusCode

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from starlette.testclient import TestClient

_TEST_DATA = [
    {"workflow": p["workflow"]}  # type: ignore[index]
    for p in [LAND_COVER_CHANGE_DETECTION_PRESET_SPEC, NDVI_CLIP_PRESET, NDVI_PRESET]
]
_TEST_IDS = ["lulc", "ndvi-clip-reproject", "simple-ndvi"]


@pytest.mark.parametrize(
    "preset_request_body",
    _TEST_DATA,
    ids=_TEST_IDS,
)
def test_ws_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    client: TestClient,
    mocked_ades_factory_ws: MagicMock,  # noqa: ARG001
    mocked_token_client_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
    preset_request_body: dict[str, Any],
) -> None:
    # Act
    with client.websocket_connect(
        url="/api/v1.2/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json(preset_request_body)

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
    client: TestClient,
    mocked_ades_factory_ws: MagicMock,  # noqa: ARG001
    mocked_token_client_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(NDVI_CLIP_PRESET)
    preset_request_body["workflow"]["ndvi"]["inputs"]["stac_collection"] = "dummy-collection"  # type: ignore[index]

    with (  # noqa: PT012
        pytest.raises(RuntimeError),
        client.websocket_connect(
            url="/api/v1.2/action-creator/ws/submissions",
            headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        ) as websocket,
    ):
        # Send the request body (job submission)
        websocket.send_json(preset_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "collection_not_supported_error"
        assert response["result"]["detail"][0]["msg"] == (
            "Collection 'dummy-collection' cannot be used with 'raster-calculate' function! "
            "Valid options are: ['sentinel-2-l2a']."
        )
        websocket.close()


def test_ws_job_submissions_endpoint_returns_422_when_missing_geometry(
    client: TestClient,
    mocked_ades_factory_ws: MagicMock,  # noqa: ARG001
    mocked_token_client_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(NDVI_CLIP_PRESET)
    preset_request_body["workflow"]["ndvi"]["inputs"].pop("aoi")  # type: ignore[attr-defined,index]

    # Act
    with (  # noqa: PT012
        pytest.raises(RuntimeError),
        client.websocket_connect(
            url="/api/v1.2/action-creator/ws/submissions",
            headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        ) as websocket,
    ):
        # Send the request body (job submission)
        websocket.send_json(preset_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "missing_geometry_error"
        assert response["result"]["detail"][0]["msg"] == "Area of Interest is missing."


def test_ws_job_submissions_endpoint_returns_422_when_invalid_date_range_was_provided(
    client: TestClient,
    mocked_ades_factory_ws: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(NDVI_CLIP_PRESET)
    preset_request_body["workflow"]["ndvi"]["inputs"]["date_start"] = "2024-01-01T00:00:00"  # type: ignore[index]
    preset_request_body["workflow"]["ndvi"]["inputs"]["date_end"] = "2023-01-01T00:00:00"  # type: ignore[index]

    # Act
    with (  # noqa: PT012
        pytest.raises(RuntimeError),
        client.websocket_connect(
            url="/api/v1.2/action-creator/ws/submissions",
            headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        ) as websocket,
    ):
        # Send the request body (job submission)
        websocket.send_json(preset_request_body)

        # Receive the response for job submission
        response = websocket.receive_json()

        # Assert
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response["result"]["detail"][0]["loc"] == ["body", "preset_function"]
        assert response["result"]["detail"][0]["type"] == "invalid_date_range_error"
        assert response["result"]["detail"][0]["msg"] == "End date cannot be before start date."
