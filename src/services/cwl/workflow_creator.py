from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, ClassVar

import yaml

from src.api.v1_2.action_creator.schemas.workflow_tasks import SPECTRAL_INDEX_TASK_IDS
from src.utils.names import generate_random_name

_BASE_APP_CWL_FP = Path(__file__).resolve().parent / "app.cwl"
_FUNCTION_REGISTRY_DIR = Path(__file__).parent / "function_registry"


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
        "cya": "spectral-index.yaml",
        "cdom": "spectral-index.yaml",
        "doc": "spectral-index.yaml",
        "sar-water-mask": "spectral-index.yaml",
        "defra-calibrate": "defra-calibrate.yaml",
        "clip": "clip.yaml",
        "reproject": "reproject.yaml",
        "stac-join": "stac-join.yaml",
        "summarize-class-statistics": "summarize-class-statistics.yaml",
    }

    @classmethod
    def get_task_spec(cls, function_identifier: str, id_override: str | None = None) -> dict[str, Any]:
        fp = _FUNCTION_REGISTRY_DIR / cls._identifier_to_cwl_lookup[function_identifier]
        spec: dict[str, Any] = yaml.safe_load(fp.open(encoding="utf-8"))
        spec["id"] = id_override or function_identifier
        return spec

    @classmethod
    def resolve_input(cls, task_input: dict[str, Any]) -> Any:
        sanitized_input_val = [i for i in task_input["value"] if i not in {"inputs", "functions", "outputs"}]
        if "inputs" in task_input["value"]:
            return "/".join(sanitized_input_val)
        return {"source": "/".join(sanitized_input_val)}

    @classmethod
    def wf_cwl_from_json_graph(cls, wf_spec: dict[str, Any]) -> list[dict[str, Any]]:
        # Keep copy of inputs for job execution
        user_inputs = deepcopy(wf_spec["inputs"])

        # Resolve WF specs
        wf_inputs = {}
        wf_outputs = {}
        wf_steps = {}

        max_ram = 1024
        max_cpu = 1

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

                wf_steps[task_id]["in"][input_id] = cls.resolve_input(task_input)  # type: ignore[index]

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

        # Build tasks
        tasks = [
            cls.get_task_spec(func_spec["identifier"], id_override=task_id)
            for task_id, func_spec in wf_spec["functions"].items()
        ]

        for task in tasks:
            max_ram = max(max_ram, task["requirements"]["ResourceRequirement"]["ramMax"])
            max_cpu = max(max_ram, task["requirements"]["ResourceRequirement"]["coresMax"])

        wf_name = generate_random_name()
        return [
            {
                "class": "Workflow",
                "id": wf_name,
                "label": f"AC Workflow {wf_name}",
                "doc": f'AC Workflow that uses {user_inputs["dataset"]} STAC collection '
                f'to execute following tasks: {list(wf_spec["functions"])}',
                "requirements": {"ResourceRequirement": {"coresMax": max_cpu, "ramMax": max_ram}},
                "inputs": wf_inputs,
                "outputs": wf_outputs,
                "steps": wf_steps,
            },
            *tasks,
        ]

    @classmethod
    def cwl_from_wf_spec(cls, wf_spec: dict[str, Any]) -> str:
        # Build full WF app
        app_spec = yaml.safe_load(_BASE_APP_CWL_FP.open(encoding="utf-8"))
        app_spec["$graph"] = cls.wf_cwl_from_json_graph(wf_spec)
        return yaml.dump(app_spec, sort_keys=False, indent=2)
