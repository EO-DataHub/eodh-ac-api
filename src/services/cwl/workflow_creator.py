from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, ClassVar

import yaml

_BASE_APP_CWL_FP = Path(__file__).resolve().parent / "app.cwl"
_FUNCTION_REGISTRY_DIR = Path(__file__).parent / "function_registry"


class WorkflowCreator:
    _identifier_to_cwl_lookup: ClassVar[dict[str, Any]] = {
        "s1-ds-query": "ds-query.yaml",
        "s2-ds-query": "ds-query.yaml",
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
        "summarize-class-statistics": "summarize-class-statistics.yaml",
    }

    @classmethod
    def get_task_spec(cls, function_identifier: str, id_override: str | None = None) -> dict[str, Any]:
        fp = _FUNCTION_REGISTRY_DIR / cls._identifier_to_cwl_lookup[function_identifier]
        spec: dict[str, Any] = yaml.safe_load(fp.open(encoding="utf-8"))
        spec["id"] = id_override or function_identifier
        return spec

    @classmethod
    def wf_class_from_json_graph(cls, wf_spec: dict[str, Any]) -> dict[str, Any]:
        # Keep copy of inputs for job execution
        user_inputs = deepcopy(wf_spec["inputs"])

        # Resolve WF inputs/outputs
        wf_inputs = {}
        wf_outputs = {}

        for wf_id in wf_spec["inputs"]:
            wf_inputs[wf_id] = {
                "label": wf_id,
                "doc": wf_id,
                "type": "string",
            }

        for task_id, task in wf_spec["functions"].items():
            for input_id, task_input in task["inputs"].items():
                if task_input["$type"] != "atom":
                    continue
                wf_inputs[input_id] = {
                    "label": input_id,
                    "doc": input_id,
                    "type": "string",
                }
                user_inputs[f"{task_id}/{input_id}"] = task_input["value"]

            for output_id, task_output in task["outputs"].items():
                if task_output.get("$type") is None or task_output.get("$type") != "ref":
                    continue
                wf_outputs[output_id] = {
                    "id": output_id,
                    "type": "Directory",
                    "outputSource": f"{task_id}/{output_id}",
                }

        # TODO:
        #   Generate some meaningful ID
        #   Generate label
        #   Generate doc
        #   Generate requirements
        #   Generate steps section

        return {
            "class": "Workflow",
            "id": "workflow",
            "label": "workflow",
            "doc": "workflow",
            "requirements": {"ResourceRequirement": {"coresMax": 1, "ramMax": 1024}},
            "inputs": wf_inputs,
            "outputs": wf_outputs,
        }

    @classmethod
    def cwl_from_wf_spec(cls, wf_spec: dict[str, Any]) -> str:
        # Build WF spec
        wf_class = cls.wf_class_from_json_graph(wf_spec)

        # Build tasks
        tasks = [
            cls.get_task_spec(func_spec["identifier"], id_override=task_id)
            for task_id, func_spec in wf_spec["functions"].items()
        ]

        # Build full WF app
        app_spec = yaml.safe_load(_BASE_APP_CWL_FP.open(encoding="utf-8"))
        app_spec["$graph"] = [wf_class, *tasks]
        return yaml.dump(app_spec, sort_keys=False, indent=2)
