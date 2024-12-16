from __future__ import annotations

import operator
from pathlib import Path
from typing import Any

import pytest
from matplotlib import pyplot as plt
from pydantic import ValidationError

from src.api.v1_2.action_creator.schemas.presets import (
    AREA_TOO_BIG_PRESET,
    COLLECTION_NOT_SUPPORTED_PRESET,
    CYCLE_DETECTED_PRESET,
    DISJOINED_SUBGRAPH_EXIST_PRESET,
    EXAMPLE_WORKFLOWS,
    INVALID_DATE_RANGE_PRESET,
    INVALID_PATH_REFERENCE_PRESET,
    INVALID_TASK_ORDER_PRESET,
    SELF_LOOP_DETECTED_PRESET,
    TASKS_HAVE_NO_OUTPUTS_MAPPING_PRESET,
    TOO_MANY_TASKS_PRESET,
    WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET,
)
from src.api.v1_2.action_creator.schemas.workflows import WorkflowSpec, visualize_workflow_graph, wf_as_networkx_graph


def test_should_raise_ex_if_area_too_big() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Area exceeds"):
        WorkflowSpec(**AREA_TOO_BIG_PRESET)


def test_should_raise_ex_if_task_does_not_support_collection() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="cannot be used with data coming from",
    ):
        WorkflowSpec(**COLLECTION_NOT_SUPPORTED_PRESET)


def test_should_raise_ex_if_invalid_date_range() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="End date cannot be before start date"):
        WorkflowSpec(**INVALID_DATE_RANGE_PRESET)


def test_should_raise_ex_if_too_many_tasks() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Maximum number of tasks exceeded"):
        WorkflowSpec(**TOO_MANY_TASKS_PRESET)


def test_should_raise_ex_if_last_tasks_have_no_outputs_mapping() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Those functions are wasted computations. Please ensure that their outputs map to workflow outputs.",
    ):
        WorkflowSpec(**TASKS_HAVE_NO_OUTPUTS_MAPPING_PRESET)


def test_should_raise_ex_if_invalid_task_order() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Task 'savi' with identifier 'functions.savi' cannot be used with",
    ):
        WorkflowSpec(**INVALID_TASK_ORDER_PRESET)


def test_should_raise_ex_if_wf_output_not_mapped_to_task_result() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Please map which function outputs should be used for those workflow outputs.",
    ):
        WorkflowSpec(**WF_OUTPUT_NOT_MAPPED_TO_TASK_RESULT_PRESET)


def test_should_raise_ex_if_invalid_path_reference() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Invalid reference path:"):
        WorkflowSpec(**INVALID_PATH_REFERENCE_PRESET)


def test_should_raise_ex_if_self_loop_detected() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Workflow specification cannot contain cycles or self loops, but following cycles were found",
    ):
        WorkflowSpec(**SELF_LOOP_DETECTED_PRESET)


def test_should_raise_ex_if_cycle_detected() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Workflow specification cannot contain cycles or self loops, but following cycles were found",
    ):
        WorkflowSpec(**CYCLE_DETECTED_PRESET)


def test_should_raise_ex_if_disjoined_subgraph_exist() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="The workflow specification must be a single, fully connected directed acyclic graph. "
        "Subgraphs found: 2.",
    ):
        WorkflowSpec(**DISJOINED_SUBGRAPH_EXIST_PRESET)


@pytest.mark.parametrize(
    "wf_spec",
    list(EXAMPLE_WORKFLOWS.items()),
    ids=operator.itemgetter(0),
)
def test_example_workflows(wf_spec: tuple[str, dict[str, Any]]) -> None:
    WorkflowSpec(**wf_spec[1])


@pytest.mark.parametrize(
    "wf_spec_id_tuple",
    list(EXAMPLE_WORKFLOWS.items()),
    ids=operator.itemgetter(0),
)
def test_wf_visualization(wf_spec_id_tuple: tuple[str, dict[str, Any]], tmp_path: Path) -> None:
    wf_id, wf_spec = wf_spec_id_tuple
    g = wf_as_networkx_graph(wf_spec, directed=True)
    fig = visualize_workflow_graph(g, figsize=(15, 9) if wf_id != "advanced-water-quality" else (15, 12))
    fig.savefig(tmp_path / f"workflow-{wf_id}.png")
    plt.close(fig)
