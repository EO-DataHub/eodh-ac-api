from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from src.api.v1_2.action_creator.schemas.presets import (
    EXAMPLE_WORKFLOWS,
    LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
    NDVI_WORKFLOW_SPEC,
)
from src.api.v1_2.action_creator.schemas.workflows import WorkflowSpec
from src.consts.geometries import UK_AOI


@pytest.fixture
def workflow_spec() -> dict[str, Any]:
    return LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC.copy()


def test_should_raise_ex_if_area_too_big(workflow_spec: dict[str, Any]) -> None:
    # Arrange
    workflow_spec["inputs"]["area"] = UK_AOI

    # Act & Assert
    with pytest.raises(ValidationError, match="Area exceeds"):
        WorkflowSpec(**workflow_spec)


def test_should_raise_ex_if_step_does_not_support_collection() -> None:
    # Arrange
    wf_spec = NDVI_WORKFLOW_SPEC.copy()
    wf_spec["functions"].pop("reproject")
    wf_spec["functions"]["summarize"] = {
        "identifier": "summarize-class-statistics",
        "inputs": {
            "data_dir": {
                "$type": "ref",
                "value": ["functions", "ndvi", "outputs", "results"],
            },
        },
        "outputs": {
            "results": {"$type": "ref", "value": ["outputs", "results"]},
        },
    }
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="cannot be used with data coming from",
    ):
        WorkflowSpec(**wf_spec)


def test_should_raise_ex_if_invalid_date_range(workflow_spec: dict[str, Any]) -> None:
    # Arrange
    workflow_spec["inputs"]["date_start"] = "2003-01-01"
    workflow_spec["inputs"]["date_end"] = "2000-01-01"

    # Act & Assert
    with pytest.raises(ValidationError, match="End date cannot be before start date"):
        WorkflowSpec(**workflow_spec)


def test_should_raise_ex_if_invalid_step_order() -> None:
    raise NotImplementedError


def test_should_raise_ex_if_wf_output_not_mapped_to_step_result() -> None:
    raise NotImplementedError


def test_should_raise_ex_if_invalid_path_reference() -> None:
    raise NotImplementedError


def test_should_raise_ex_if_cycle_detected() -> None:
    raise NotImplementedError


@pytest.mark.parametrize(
    "wf_spec",
    list(EXAMPLE_WORKFLOWS.items()),
    ids=lambda x: x[0],
)
def test_example_workflows(wf_spec: tuple[str, dict[str, Any]]) -> None:
    WorkflowSpec(**wf_spec[1])
