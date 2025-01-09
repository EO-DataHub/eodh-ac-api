from __future__ import annotations

from collections.abc import Hashable

from pydantic import BaseModel
from pydantic_core import PydanticCustomError


class ErrorResponse(BaseModel):
    detail: str


class CycleOrSelfLoopError:
    @classmethod
    def make(cls, cycles: list[list[str]]) -> PydanticCustomError:
        formatted_cycles = [" -> ".join(c) + f" -> {c[0]}" for c in cycles]
        return PydanticCustomError(
            "cycle_or_self_loop_detected_error",
            "Workflow specification cannot contain cycles or self loops, but following cycles were found: {cycles}.",
            {
                "cycles": formatted_cycles,
            },
        )


class DisjoinedSubgraphsError:
    @classmethod
    def make(cls, subgraphs: int) -> PydanticCustomError:
        return PydanticCustomError(
            "disjoined_subgraphs_detected_error",
            "The workflow specification must be a single, fully connected directed acyclic graph. "
            "Subgraphs found: {subgraphs}.",
            {
                "subgraphs": subgraphs,
            },
        )


class DanglingFunctionsError:
    @classmethod
    def make(cls, dangling_functions: list[str]) -> PydanticCustomError:
        return PydanticCustomError(
            "dangling_functions_detected_error",
            (
                "Workflow functions: {dangling_functions} have outputs without any mapping to workflow outputs. "
                "Those functions are wasted computations. Please ensure that their outputs map to workflow outputs."
            ),
            {
                "dangling_functions": dangling_functions,
            },
        )


class TaskOutputWithoutMappingError:
    @classmethod
    def make(cls, dangling_outputs: list[str]) -> PydanticCustomError:
        return PydanticCustomError(
            "task_output_without_mapping_detected_error",
            (
                "Workflow outputs: {dangling_outputs} are not mapped to function outputs. "
                "Please map which function outputs should be used for those workflow outputs."
            ),
            {
                "dangling_outputs": dangling_outputs,
            },
        )


class InvalidTaskOrderError:
    @classmethod
    def make(cls, function_identifier: str, target_id: str) -> PydanticCustomError:
        return PydanticCustomError(
            "invalid_task_order_detected_error",
            (
                "Task '{function_identifier}' with identifier '{target_id}' cannot be used "
                "with outputs from preceding tasks."
            ),
            {
                "function_identifier": function_identifier,
                "target_id": target_id,
            },
        )


class CollectionNotSupportedForTaskError:
    @classmethod
    def make(cls, invalid_tasks: list[str], dataset: str) -> PydanticCustomError:
        return PydanticCustomError(
            "collection_not_supported_for_task_error",
            "Functions: {invalid_tasks} cannot be used with data coming from '{dataset}' dataset.",
            {"invalid_tasks": invalid_tasks, "dataset": dataset},
        )


class InvalidReferencePathError:
    @classmethod
    def make(cls, path: list[Hashable], invalid_key: Hashable) -> PydanticCustomError:
        return PydanticCustomError(
            "invalid_reference_path_error",
            "Invalid reference path: {path}. Key '{invalid_key}' does not exist in the Workflow definition.",
            {
                "path": path,
                "invalid_key": invalid_key,
            },
        )


class MaximumNumberOfTasksExceededError:
    @classmethod
    def make(cls, max_tasks_num: int) -> PydanticCustomError:
        return PydanticCustomError(
            "maximum_number_of_tasks_exceeded_error",
            "Maximum number of tasks exceeded. Currently we only support maximum of {max_tasks_num} tasks.",
            {"max_tasks_num": max_tasks_num},
        )


class WorkflowIdentifierCollisionError:
    @classmethod
    def make(cls, identifier: str) -> PydanticCustomError:
        return PydanticCustomError(
            "workflow_identifier_collision_error",
            "The workflow identifier '{identifier}' collides with a function with the same identifier.",
            {"identifier": identifier},
        )
