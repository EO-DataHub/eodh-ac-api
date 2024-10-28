from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Annotated, Any

from geojson_pydantic import Polygon
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from src.api.v1_1.action_creator.schemas.workflow_steps import DirectoryOutputs, TWorkflowStep
from src.services.validation_utils import aoi_must_be_present, ensure_area_smaller_than, validate_date_range


class MainWorkflowInputs(BaseModel):
    area: Annotated[Polygon | None, Field(None, validate_default=True)]
    date_start: datetime | None = None
    date_end: datetime | None = None
    dataset: str
    dataset_advanced_settings: dict[str, int | float | str | bool | None] | None = None

    @field_validator("area", mode="before")
    @classmethod
    def validate_aoi(cls, v: dict[str, Any] | None = None) -> dict[str, Any]:
        # Ensure AOI provided
        aoi_must_be_present(v)

        # Ensure AOI does not exceed area limit
        geom_to_check = Polygon(**v)
        ensure_area_smaller_than(geom_to_check.model_dump())

        return v  # type: ignore[return-value]

    @field_validator("date_end", mode="after")
    @classmethod
    def validate_date_range(cls, date_end: datetime | None, info: ValidationInfo) -> datetime | None:
        date_start = info.data.get("date_start")
        validate_date_range(date_start=date_start, date_end=date_end)
        return date_end


class ExtendedDict(dict[str, Any]):
    """Extended dictionary that supports nested key lookup using list of keys.

    Changes a normal dict into one where you can hand a list
    as first argument to .get() and it will do a recursive lookup

    Examples:
        >> result = x.get(['a', 'b', 'c'], default_val)

    """

    def multi_level_get(self, path: list[str]) -> Any:
        # assume that the key is a list of recursively accessible dicts
        def get_one_level(key_list: list[str], level: int, context: dict[str, Any]) -> Any:
            if level >= len(key_list):
                if level > len(key_list):
                    raise IndexError
                return context[key_list[level - 1]]
            return get_one_level(key_list, level + 1, context[key_list[level - 1]])

        try:
            return get_one_level(path, 1, self)
        except KeyError as ex:
            msg = f"Invalid reference path: {path}. Key '{ex.args[0]}' does not exist in the Workflow definition."
            raise ValueError(msg) from ex


def resolve_references_and_atom_values(data: dict[str, Any]) -> dict[str, Any]:
    """Replaces references and atomics in the function inputs with actual values.

    Args:
        data: The data dictionary.

    Returns:
        A new data dictionary with resolved inputs.

    """
    resolved_functions: dict[str, Any] = deepcopy(data)
    extended_dict = ExtendedDict(data)
    for f_id, f_spec in data["functions"].items():
        resolved_inputs: dict[str, Any] = {}
        for input_id, input_val in f_spec["inputs"].items():
            if isinstance(input_val, dict) and input_val.get("$type") == "ref":
                resolved_inputs[input_id] = extended_dict.multi_level_get(input_val["value"])
            elif isinstance(input_val, dict) and input_val.get("$type") == "atom":
                resolved_inputs[input_id] = input_val["value"]
            else:
                resolved_inputs[input_id] = input_val
        resolved_functions["functions"][f_id]["inputs"] = resolved_inputs
        resolved_functions["functions"][f_id]["outputs"] = data["functions"][f_id]["outputs"]
    return resolved_functions


class WorkflowSpec(BaseModel):
    inputs: MainWorkflowInputs
    outputs: DirectoryOutputs
    functions: dict[str, TWorkflowStep]

    @model_validator(mode="before")
    @classmethod
    def validate_workflow(cls, v: dict[str, Any]) -> dict[str, Any]:
        return resolve_references_and_atom_values(v)


class WorkflowSubmissionRequest(BaseModel):
    workflow: WorkflowSpec
