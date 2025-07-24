from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from src.api.v1_3.action_creator.schemas.presets import (
    ADVANCED_WATER_QUALITY_WORKFLOW_SPEC,
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
    WF_ID_COLLISION_PRESET,
    WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET,
)
from tests.fakes.ades import FakeADESClient, fake_ades_client_factory
from tests.fakes.ws_token_client import FakeTokenClient

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mocked_ades_factory() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_3.action_creator.routes.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock


@pytest.fixture
def mocked_token_client_factory() -> Generator[MagicMock, None]:
    token_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_3.action_creator.routes.ws_token_session_auth_client_factory",
    ) as token_client_factory_mock:
        token_client_factory_mock.return_value = FakeTokenClient()
        yield token_client_factory_mock


TEST_WORKFLOWS = {
    "land-cover": {
        "value": LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
        "should_raise": False,
    },
    "water-quality": {
        "value": WATER_QUALITY_WORKFLOW_SPEC,
        "should_raise": False,
    },
    "advanced-water-quality": {
        "value": ADVANCED_WATER_QUALITY_WORKFLOW_SPEC,
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
    "err-wf-id-collision": {
        "error": "workflow_identifier_collision_error",
        "should_raise": True,
        "value": WF_ID_COLLISION_PRESET,
    },
}
