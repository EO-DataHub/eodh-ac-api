from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from flaky import flaky
from starlette import status

from src.api.v1_1.action_creator.schemas import ActionCreatorJob
from src.consts.presets import LAND_COVER_CHANGE_DETECTION_PRESET_SPEC
from src.services.ades.schemas import StatusCode

if TYPE_CHECKING:
    from starlette.testclient import TestClient


@flaky(max_runs=3)
def test_ws_job_submissions_endpoint_returns_valid_response_when_all_is_ok(
    client: TestClient,
    auth_token_func_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(LAND_COVER_CHANGE_DETECTION_PRESET_SPEC)
    preset_request_body["workflow"]["land-cover-change-detection"]["inputs"]["stac_collection"] = "clms-corinelc"  # type: ignore[index]

    # Act
    with client.websocket_connect(
        url="/api/v1.1/action-creator/ws/submissions",
        headers={"Authorization": f"Bearer {auth_token_func_scoped}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json({"workflow": preset_request_body["workflow"]})

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


@flaky(max_runs=3)
def test_ws_job_status_endpoint_returns_valid_response_when_all_is_ok(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    preset_request_body = deepcopy(LAND_COVER_CHANGE_DETECTION_PRESET_SPEC)
    preset_request_body["workflow"]["land-cover-change-detection"]["inputs"]["stac_collection"] = "clms-corinelc"  # type: ignore[index]
    response = client.post(
        "/api/v1.1/action-creator/submissions",
        json=preset_request_body,
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    job_spec = ActionCreatorJob(**response.json())

    # Act
    with client.websocket_connect(
        url="/api/v1.1/action-creator/ws/submission-status",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    ) as websocket:
        # Send the request body (job submission)
        websocket.send_json({"submission_id": job_spec.submission_id})

        # Receive the response for job submission
        job_response = websocket.receive_json()

        # Assert final job status
        assert job_response["status_code"] == status.HTTP_200_OK
        assert job_response["result"]["status"] == StatusCode.successful.value
        assert job_response["result"]["finished_at"] is not None
