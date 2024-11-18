from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import pytest
import yaml

from src.api.v1_2.action_creator.schemas.presets import EXAMPLE_WORKFLOWS
from src.api.v1_2.action_creator.schemas.workflow_tasks import FUNCTIONS_REGISTRY
from src.services.cwl.workflow_creator import WorkflowCreator

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "function_identifier",
    list(FUNCTIONS_REGISTRY.keys()),
)
def test_function_registry_should_load_task_spec(function_identifier: str) -> None:
    # Act
    spec = WorkflowCreator.get_task_spec(function_identifier)

    # Assert
    assert spec["id"] == function_identifier


@pytest.mark.parametrize(
    "function_identifier",
    list(FUNCTIONS_REGISTRY.keys()),
)
def test_function_registry_should_load_task_spec_with_id_override(function_identifier: str) -> None:
    # Arrange
    id_override = str(uuid4())

    # Act
    spec = WorkflowCreator.get_task_spec(function_identifier, id_override=id_override)

    # Assert
    assert spec["id"] == id_override


@pytest.mark.parametrize(
    ("identifier", "wf_spec"),
    list(EXAMPLE_WORKFLOWS.items()),
)
def test_presets(identifier: str, wf_spec: dict[str, Any]) -> None:  # noqa: ARG001
    # Act
    app_cwl = WorkflowCreator.cwl_from_wf_spec(wf_spec)

    # Assert
    app_spec = yaml.safe_load(app_cwl)
    assert app_spec["$graph"] is not None
    assert len(app_spec["$graph"]) == len(wf_spec["functions"]) + 1


@pytest.mark.parametrize(
    ("identifier", "wf_spec"),
    list(EXAMPLE_WORKFLOWS.items()),
)
def test_generated_cwl_spec(identifier: str, wf_spec: dict[str, Any], tmp_path: Path) -> None:
    # Act
    app_cwl = WorkflowCreator.cwl_from_wf_spec(wf_spec)

    # Assert
    tmp_cwl_fp = tmp_path / f"{identifier}.yaml"
    tmp_cwl_fp.write_text(app_cwl, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        ["cwltool", "--validate", tmp_cwl_fp.as_posix()],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0