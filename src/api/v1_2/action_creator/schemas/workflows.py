from __future__ import annotations

from collections.abc import Hashable
from copy import deepcopy
from datetime import datetime
from typing import Annotated, Any

import networkx as nx
from geojson_pydantic import Polygon
from matplotlib import pyplot as plt
from networkx.classes import DiGraph, Graph
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from src.api.v1_2.action_creator.schemas.errors import (
    CollectionNotSupportedForTaskError,
    CycleOrSelfLoopError,
    DanglingFunctionsError,
    DisjoinedSubgraphsError,
    InvalidReferencePathError,
    InvalidTaskOrderError,
    MaximumNumberOfTasksExceededError,
    TaskOutputWithoutMappingError,
)
from src.api.v1_2.action_creator.schemas.workflow_tasks import (
    FUNCTIONS_REGISTRY,
    DirectoryOutputs,
    TaskCompatibility,
    TWorkflowTask,
    check_task_compatibility,
)
from src.services.validation_utils import aoi_must_be_present, ensure_area_smaller_than, validate_date_range

MAX_WF_TASKS = 15


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


class ExtendedDict(dict[Hashable, Any]):
    """Extended dictionary that supports nested key lookup using list of keys.

    Changes a normal dict into one where you can hand a list
    as first argument to .get() and it will do a recursive lookup

    Examples:
        >> result = x.get(['a', 'b', 'c'], default_val)

    """

    def multi_level_get(self, path: list[Hashable]) -> Any:
        # assume that the key is a list of recursively accessible dicts
        def get_one_level(key_list: list[Hashable], level: int, context: dict[Hashable, Any]) -> Any:
            if level >= len(key_list):
                if level > len(key_list):
                    raise IndexError
                return context[key_list[level - 1]]
            return get_one_level(key_list, level + 1, context[key_list[level - 1]])

        try:
            return get_one_level(path, 1, self)
        except KeyError as ex:
            raise InvalidReferencePathError.make(path=path, invalid_key=ex.args[0]) from ex


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
        resolved_outputs: dict[str, Any] = {}
        for kind, collection in zip(["inputs", "outputs"], [resolved_inputs, resolved_outputs]):
            for id_, val in f_spec[kind].items():
                if isinstance(val, dict) and val.get("$type") == "ref":
                    collection[id_] = extended_dict.multi_level_get(val["value"])
                elif isinstance(val, dict) and val.get("$type") == "atom":
                    collection[id_] = val["value"]
                else:
                    collection[id_] = val
        resolved_functions["functions"][f_id]["inputs"] = resolved_inputs
        resolved_functions["functions"][f_id]["outputs"] = resolved_outputs
    return resolved_functions


def check_for_max_tasks(data: dict[str, Any], max_tasks: int = MAX_WF_TASKS) -> None:
    if len(data["functions"]) > max_tasks:
        raise MaximumNumberOfTasksExceededError.make(max_tasks_num=max_tasks)


def wf_as_networkx_graph(data: dict[str, Any], *, directed: bool = False) -> nx.Graph | nx.DiGraph:
    g = nx.DiGraph() if directed else nx.Graph()
    g.add_nodes_from((f"inputs.{k}", {"value": v}) for k, v in data["inputs"].items())
    g.add_nodes_from((f"functions.{k}", v) for k, v in data["functions"].items())
    g.add_nodes_from((f"outputs.{k}", {"value": v}) for k, v in data["outputs"].items())

    edges: list[tuple[str, str]] = []
    for f_id, f_spec in data["functions"].items():
        for input_val in f_spec["inputs"].values():
            if isinstance(input_val, dict) and input_val.get("$type") == "ref":
                edges.append((".".join(input_val["value"][:2]), f"functions.{f_id}"))  # noqa: PERF401
        for output_val in f_spec["outputs"].values():
            if isinstance(output_val, dict) and output_val.get("$type") == "ref":
                edges.append((f"functions.{f_id}", ".".join(output_val["value"][:2])))  # noqa: PERF401
    g.add_edges_from(edges)

    return g


def visualize_workflow_graph(
    g: nx.Graph,
    figsize: tuple[float, float] = (15, 9),
    node_size: int = 2000,
    **kwargs: Any,
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    plot_options = {"node_size": node_size, "with_labels": True}
    pos = nx.nx_agraph.graphviz_layout(g, prog="dot")
    nx.draw_networkx(g, pos=pos, ax=ax, **plot_options, **kwargs)
    return fig


def check_for_cycles(g: nx.DiGraph) -> None:
    cycles = sorted(nx.simple_cycles(g))
    if cycles:
        raise CycleOrSelfLoopError.make(cycles)


def check_for_disjoined_subgraphs(g: nx.Graph) -> None:
    if (n := nx.number_connected_components(g)) > 1:
        raise DisjoinedSubgraphsError.make(subgraphs=n)


def check_for_dangling_function(g: DiGraph) -> None:
    dangling_functions = [x for x in g.nodes() if g.out_degree(x) == 0 and g.in_degree(x) == 1 and "functions." in x]
    if len(dangling_functions) > 0:
        raise DanglingFunctionsError.make(dangling_functions=dangling_functions)


def check_task_outputs_mapped_to_wf_outputs(g: nx.DiGraph) -> None:
    dangling_outputs = [x for x in g.nodes() if g.out_degree(x) == 0 and g.in_degree(x) == 0 and "outputs." in x]
    if len(dangling_outputs) > 0:
        raise TaskOutputWithoutMappingError.make(dangling_outputs=dangling_outputs)


def check_task_order(g: nx.DiGraph) -> None:
    # TODO extend this to incorporate all possible vertex paris
    for src_id, target_id in g.edges():
        if "inputs" in src_id or "outputs" in src_id:
            continue
        if "inputs" in target_id or "outputs" in target_id:
            continue
        src, target = g.nodes[src_id], g.nodes[target_id]
        if check_task_compatibility(src["identifier"], target["identifier"]) == TaskCompatibility.no:
            raise InvalidTaskOrderError.make(function_identifier=target["identifier"], target_id=target_id)


def check_task_collection_support(data: dict[str, Any]) -> None:
    ds = data["inputs"]["dataset"]
    invalid_tasks = []
    for task in data["functions"].values():
        func_spec = FUNCTIONS_REGISTRY[task["identifier"]]
        if ds not in func_spec["compatible_input_datasets"]:
            invalid_tasks.append(task["identifier"])
    if invalid_tasks:
        raise CollectionNotSupportedForTaskError.make(invalid_tasks=invalid_tasks, dataset=ds)


class WorkflowSpec(BaseModel):
    inputs: MainWorkflowInputs
    outputs: DirectoryOutputs
    functions: dict[str, TWorkflowTask]

    @model_validator(mode="before")
    @classmethod
    def validate_workflow_before_instantiation(cls, v: dict[str, Any]) -> dict[str, Any]:
        check_for_max_tasks(v)
        check_task_collection_support(v)
        resolved = resolve_references_and_atom_values(v)
        dg: DiGraph = wf_as_networkx_graph(v, directed=True)
        g: Graph = wf_as_networkx_graph(v)
        check_for_cycles(dg)
        check_task_outputs_mapped_to_wf_outputs(dg)
        check_for_disjoined_subgraphs(g)
        check_for_dangling_function(dg)
        check_task_order(dg)
        return resolved


class WorkflowSubmissionRequest(BaseModel):
    workflow: WorkflowSpec
