from __future__ import annotations

import operator
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from matplotlib import pyplot as plt
from pydantic import ValidationError

from src.api.v1_2.action_creator.schemas.presets import (
    EXAMPLE_WORKFLOWS,
    LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC,
    NDVI_WORKFLOW_SPEC,
)
from src.api.v1_2.action_creator.schemas.workflows import WorkflowSpec, visualize_workflow_graph, wf_as_networkx_graph
from src.consts.geometries import UK_AOI


@pytest.fixture
def lulc_wf() -> dict[str, Any]:
    return deepcopy(LAND_COVER_CHANGE_DETECTION_WORKFLOW_SPEC)


@pytest.fixture
def wf() -> dict[str, Any]:
    return deepcopy(NDVI_WORKFLOW_SPEC)


def test_should_raise_ex_if_area_too_big(wf: dict[str, Any]) -> None:
    # Arrange
    wf["inputs"]["area"] = UK_AOI

    # Act & Assert
    with pytest.raises(ValidationError, match="Area exceeds"):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_task_does_not_support_collection(wf: dict[str, Any]) -> None:
    # Arrange
    wf["functions"].pop("reproject")
    wf["functions"]["summarize"] = {
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
        WorkflowSpec(**wf)


def test_should_raise_ex_if_invalid_date_range(wf: dict[str, Any]) -> None:
    # Arrange
    wf["inputs"]["date_start"] = "2003-01-01"
    wf["inputs"]["date_end"] = "2000-01-01"

    # Act & Assert
    with pytest.raises(ValidationError, match="End date cannot be before start date"):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_too_many_tasks(wf: dict[str, Any]) -> None:
    # Arrange
    for i in range(10):
        wf["functions"][f"ndvi-{i}"] = wf["functions"]["ndvi"]

    # Act & Assert
    with pytest.raises(ValidationError, match="Maximum number of tasks exceeded"):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_last_tasks_have_no_outputs_mapping(wf: dict[str, Any]) -> None:
    # Arrange
    wf["functions"]["ndvi-2"] = {
        "identifier": "ndvi",
        "inputs": {
            "data_dir": {
                "$type": "ref",
                "value": ["functions", "query", "outputs", "results"],
            },
        },
        "outputs": {"results": {"name": "results", "type": "directory"}},
    }

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Those functions are wasted computations. Please ensure that their outputs map to workflow outputs.",
    ):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_invalid_task_order(wf: dict[str, Any]) -> None:
    # Arrange
    wf["functions"]["savi"] = deepcopy(wf["functions"]["ndvi"])
    wf["functions"]["savi"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "ndvi", "outputs", "results"],
    }
    wf["functions"]["savi"]["identifier"] = "savi"
    wf["functions"]["reproject"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "savi", "outputs", "results"],
    }

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Task 'savi' with identifier 'functions.savi' cannot be used with",
    ):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_wf_output_not_mapped_to_task_result(wf: dict[str, Any]) -> None:
    # Arrange
    wf["outputs"]["test_output"] = {"name": "test_output", "type": "directory"}

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Please map which function outputs should be used for those workflow outputs.",
    ):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_invalid_path_reference(wf: dict[str, Any]) -> None:
    # Arrange
    wf["functions"]["ndvi"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "invalid", "function", "ref"],
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="Invalid reference path:"):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_self_loop_detected(wf: dict[str, Any]) -> None:
    # Arrange
    wf["functions"]["reproject"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "reproject", "outputs", "results"],
    }

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Workflow specification cannot contain cycles or self loops, but following cycles were found",
    ):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_cycle_detected(wf: dict[str, Any]) -> None:
    # Arrange
    wf["functions"]["ndvi"]["inputs"]["data_dir"] = {
        "$type": "ref",
        "value": ["functions", "reproject", "outputs", "results"],
    }

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Workflow specification cannot contain cycles or self loops, but following cycles were found",
    ):
        WorkflowSpec(**wf)


def test_should_raise_ex_if_disjoined_subgraph_exist(wf: dict[str, Any]) -> None:
    # Arrange
    wf["functions"]["ndvi-2"] = {
        "identifier": "ndvi",
        "inputs": {
            "data_dir": {
                "$type": "atom",
                "value": {"name": "data_dir", "type": "directory"},
            },
        },
        "outputs": {
            "results": {"$type": "atom", "value": {"name": "results", "type": "directory"}},
        },
    }

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="The workflow specification must be a single, fully connected directed acyclic graph. "
        "Subgraphs found: 2.",
    ):
        WorkflowSpec(**wf)


@pytest.mark.parametrize(
    "wf_spec",
    list(EXAMPLE_WORKFLOWS.items()),
    ids=operator.itemgetter(0),
)
def test_example_workflows(wf_spec: tuple[str, dict[str, Any]]) -> None:
    WorkflowSpec(**wf_spec[1])


def test_wf_visualization(tmp_path: Path) -> None:
    for wf_id, wf_spec in EXAMPLE_WORKFLOWS.items():
        g = wf_as_networkx_graph(wf_spec, directed=True)
        fig = visualize_workflow_graph(g)
        fig.savefig(tmp_path / f"workflow-{wf_id}.png")
        plt.close(fig)
