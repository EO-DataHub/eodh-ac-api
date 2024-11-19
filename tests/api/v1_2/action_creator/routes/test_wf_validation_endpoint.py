from __future__ import annotations

from operator import itemgetter
from typing import TYPE_CHECKING, Any

import pytest
from starlette import status

from src.api.v1_2.action_creator.schemas.presets import (
    AREA_TOO_BIG_PRESET,
    COLLECTION_NOT_SUPPORTED_PRESET,
    CYCLE_DETECTED_PRESET,
    DISJOINED_SUBGRAPH_EXIST_PRESET,
    INVALID_DATE_RANGE_PRESET,
    INVALID_PATH_REFERENCE_PRESET,
    INVALID_TASK_ORDER_PRESET,
    LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
    NDVI_WORKFLOW_SPEC,
    SELF_LOOP_DETECTED_PRESET,
    SIMPLEST_NDVI_WORKFLOW_SPEC,
    TOO_MANY_TASKS_PRESET,
    WATER_QUALITY_WORKFLOW_SPEC,
    WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET,
)
from src.api.v1_2.action_creator.schemas.workflow_tasks import WorkflowValidationResult

if TYPE_CHECKING:
    from starlette.testclient import TestClient

_TEST_WORKFLOWS = {
    "land-cover": {
        "value": LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
        "should_raise": False,
    },
    "water-quality": {
        "value": WATER_QUALITY_WORKFLOW_SPEC,
        "should_raise": False,
    },
    "simplest-ndvi": {
        "value": SIMPLEST_NDVI_WORKFLOW_SPEC,
        "should_raise": False,
    },
    "ndvi-clip-reproject": {
        "value": NDVI_WORKFLOW_SPEC,
        "should_raise": False,
    },
    "err-area-too-big": {
        "error": "area_of_interest_too_big_error",
        "should_raise": True,
        "value": AREA_TOO_BIG_PRESET,
    },
    "err-invalid-date-range": {
        "error": "invalid_date_range_error",
        "should_raise": True,
        "value": INVALID_DATE_RANGE_PRESET,
    },
    "err-invalid-dataset": {
        "error": "collection_not_supported_for_task_error",
        "should_raise": True,
        "value": COLLECTION_NOT_SUPPORTED_PRESET,
    },
    "err-invalid-reference": {
        "error": "invalid_reference_path_error",
        "should_raise": True,
        "value": INVALID_PATH_REFERENCE_PRESET,
    },
    "err-invalid-task-order": {
        "error": "invalid_task_order_detected_error",
        "should_raise": True,
        "value": INVALID_TASK_ORDER_PRESET,
    },
    "err-too-many-tasks": {
        "error": "maximum_number_of_tasks_exceeded_error",
        "should_raise": True,
        "value": TOO_MANY_TASKS_PRESET,
    },
    "err-tasks-have-no-outputs-mapping": {
        "error": "task_output_without_mapping_detected_error",
        "should_raise": True,
        "value": WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET,
    },
    "err-wf-output-not-mapped-to-task-result": {
        "error": "task_output_without_mapping_detected_error",
        "should_raise": True,
        "value": WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET,
    },
    "err-self-loop-detected": {
        "error": "cycle_or_self_loop_detected_error",
        "should_raise": True,
        "value": SELF_LOOP_DETECTED_PRESET,
    },
    "err-cycle-detected": {
        "error": "cycle_or_self_loop_detected_error",
        "should_raise": True,
        "value": CYCLE_DETECTED_PRESET,
    },
    "err-disjoined-subgraph-exist": {
        "error": "disjoined_subgraphs_detected_error",
        "should_raise": True,
        "value": DISJOINED_SUBGRAPH_EXIST_PRESET,
    },
}


@pytest.mark.parametrize(
    "wf_spec",
    _TEST_WORKFLOWS.items(),
    ids=itemgetter(0),
)
def test_wf_validation_endpoint(wf_spec: tuple[str, dict[str, Any]], client: TestClient, auth_token: str) -> None:
    # Arrange
    _, wf = wf_spec

    # Act
    response = client.post(
        "/api/v1.2/action-creator/workflow-validation",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=wf["value"],
    )

    # Assert
    if wf["should_raise"]:
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"][0]["type"] == wf["error"]
    else:
        assert response.status_code == status.HTTP_200_OK
        WorkflowValidationResult(**response.json())
