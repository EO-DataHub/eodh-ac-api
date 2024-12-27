from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

import yaml

from src.api.v1_2.action_creator.schemas.workflow_tasks import SPECTRAL_INDEX_TASK_IDS
from src.services.ades.client import replace_placeholders_in_text
from src.utils.names import generate_random_name

_BASE_APP_CWL_FP = Path(__file__).resolve().parent / "app.cwl"
_FUNCTION_REGISTRY_DIR = Path(__file__).parent / "function_registry"


@dataclass
class CWLGraphData:
    wf_id: str
    graph: list[dict[str, Any]]
    user_inputs: dict[str, Any]


@dataclass
class WorkflowCreatorResult:
    app_spec: dict[str, Any]
    wf_id: str
    user_inputs: dict[str, Any]


class WorkflowCreator:
    _identifier_to_cwl_lookup: ClassVar[dict[str, Any]] = {
        "s1-ds-query": "s1-ds-query.yaml",
        "s2-ds-query": "s2-ds-query.yaml",
        "esa-glc-ds-query": "ds-query.yaml",
        "corine-lc-ds-query": "ds-query.yaml",
        "water-bodies-ds-query": "ds-query.yaml",
        "ndvi": "spectral-index.yaml",
        "savi": "spectral-index.yaml",
        "evi": "spectral-index.yaml",
        "ndwi": "spectral-index.yaml",
        "cya_cells": "spectral-index.yaml",
        "cdom": "spectral-index.yaml",
        "turb": "spectral-index.yaml",
        "doc": "spectral-index.yaml",
        "sar-water-mask": "spectral-index.yaml",
        "defra-calibrate": "defra-calibrate.yaml",
        "water-quality": "water-quality.yaml",
        "clip": "clip.yaml",
        "reproject": "reproject.yaml",
        "stac-join": "stac-join.yaml",
        "summarize-class-statistics": "summarize-class-statistics.yaml",
        "thumbnail": "thumbnail.yaml",
    }

    @classmethod
    def _resolve_task_spec(cls, function_identifier: str, id_override: str | None = None) -> dict[str, Any]:
        fp = _FUNCTION_REGISTRY_DIR / cls._identifier_to_cwl_lookup[function_identifier]
        spec: dict[str, Any] = yaml.safe_load(replace_placeholders_in_text(fp.read_text(encoding="utf-8")))
        spec["id"] = id_override or function_identifier
        return spec

    @classmethod
    def _resolve_input_value(cls, task_input: dict[str, Any]) -> Any:
        sanitized_input_val = [i for i in task_input["value"] if i not in {"inputs", "functions", "outputs"}]
        if "inputs" in task_input["value"]:
            return "/".join(sanitized_input_val)
        return {"source": "/".join(sanitized_input_val)}

    @classmethod
    def _resolve_wf_steps_in_out_and_user_inputs(
        cls,
        wf_spec: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        # Keep copy of inputs for job execution
        user_inputs = deepcopy(wf_spec["inputs"])
        user_inputs["area"] = json.dumps(user_inputs.pop("area"))

        # Resolve WF specs
        wf_inputs = {}
        wf_outputs = {}
        wf_steps = {}

        for wf_id in wf_spec["inputs"]:
            wf_inputs[wf_id] = {
                "label": wf_id,
                "doc": wf_id,
                "type": "string",
            }

        for task_id, task in wf_spec["functions"].items():
            wf_steps[task_id] = {"run": f"#{task_id}", "in": {}, "out": []}

            # Handle `index` input for spectral-index task
            if task["identifier"] in SPECTRAL_INDEX_TASK_IDS:
                user_inputs[f"{task_id}_index"] = task_id
                wf_inputs[f"{task_id}_index"] = {
                    "label": f"{task_id}_index",
                    "doc": f"{task_id}_index",
                    "type": "string",
                }
                wf_steps[task_id]["in"]["index"] = f"{task_id}_index"  # type: ignore[index]

            # Handle task inputs
            for input_id, task_input in task["inputs"].items():
                if task_input["$type"] == "atom":
                    user_inputs[f"{task_id}_{input_id}"] = str(task_input["value"])
                    wf_steps[task_id]["in"][input_id] = f"{task_id}_{input_id}"  # type: ignore[index]
                    wf_inputs[f"{task_id}_{input_id}"] = {
                        "label": f"{task_id}_{input_id}",
                        "doc": f"{task_id}_{input_id}",
                        "type": "string",
                    }
                    continue

                wf_steps[task_id]["in"][input_id] = cls._resolve_input_value(task_input)  # type: ignore[index]

            # Handle task outputs
            for output_id, task_output in task["outputs"].items():
                if task_output.get("$type") is None or task_output.get("$type") != "ref":
                    wf_steps[task_id]["out"].append(output_id)  # type: ignore[attr-defined]
                    continue

                wf_steps[task_id]["out"].append(output_id)  # type: ignore[attr-defined]
                wf_outputs[output_id] = {
                    "id": output_id,
                    "type": "Directory",
                    "outputSource": f"{task_id}/{output_id}",
                }

        return user_inputs, wf_inputs, wf_outputs, wf_steps

    @classmethod
    def _wf_cwl_from_json_graph(cls, wf_spec: dict[str, Any]) -> CWLGraphData:
        # Resolve user inputs, WF in/out and WF steps
        user_inputs, wf_inputs, wf_outputs, wf_steps = cls._resolve_wf_steps_in_out_and_user_inputs(wf_spec)

        # Build tasks
        tasks = [
            cls._resolve_task_spec(func_spec["identifier"], id_override=task_id)
            for task_id, func_spec in wf_spec["functions"].items()
        ]

        # Resolve WF requirements
        wf_requirements = cls._resolve_wf_requirements(tasks)

        # Build CWL Graph Data
        wf_name = wf_spec.get("identifier", generate_random_name())
        return CWLGraphData(
            wf_id=wf_name,
            graph=[
                {
                    "class": "Workflow",
                    "id": wf_name,
                    "label": f"AC Workflow {wf_name}",
                    "doc": f'AC Workflow that uses {user_inputs["dataset"]} STAC collection '
                    f'to execute following tasks: {list(wf_spec["functions"])}',
                    "requirements": wf_requirements,
                    "inputs": wf_inputs,
                    "outputs": wf_outputs,
                    "steps": wf_steps,
                },
                *tasks,
            ],
            user_inputs=user_inputs,
        )

    @classmethod
    def _resolve_wf_requirements(cls, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        min_ram = 1024
        max_ram = 1024
        min_cpu = 1
        max_cpu = 1
        for task in tasks:
            min_ram = max(min_ram, task["requirements"]["ResourceRequirement"]["ramMin"])
            max_ram = max(max_ram, task["requirements"]["ResourceRequirement"]["ramMax"])
            min_cpu = max(min_cpu, task["requirements"]["ResourceRequirement"]["coresMin"])
            max_cpu = max(max_cpu, task["requirements"]["ResourceRequirement"]["coresMax"])
        return {
            "ResourceRequirement": {
                "coresMin": min_cpu,
                "coresMax": max_cpu,
                "ramMin": min_ram,
                "ramMax": max_ram,
            },
        }

    @classmethod
    def cwl_from_wf_spec(cls, wf_spec: dict[str, Any]) -> WorkflowCreatorResult:
        """Creates CWL Workflow from a JSON Graph workflow specification.

        Args:
            wf_spec: The workflow specification as JSON Graph.

        Returns:
            ref:class::``WorkflowCreationResult`` instance

        """
        app_spec = yaml.safe_load(_BASE_APP_CWL_FP.open(encoding="utf-8"))
        wf_data = cls._wf_cwl_from_json_graph(wf_spec)
        app_spec["$graph"] = wf_data.graph
        return WorkflowCreatorResult(
            app_spec=app_spec,
            wf_id=wf_data.wf_id,
            user_inputs=wf_data.user_inputs,
        )
