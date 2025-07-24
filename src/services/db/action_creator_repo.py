from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.consts.action_creator import FUNCTIONS
from src.services.db.base import AbstractActionCreatorRepository


class ActionCreatorRepository(AbstractActionCreatorRepository):
    def __init__(self, functions: list[dict[str, Any]]) -> None:
        self._functions = functions

    def get_available_functions(
        self,
        collection: str | None = None,
    ) -> tuple[bool, list[dict[str, Any]]]:
        if collection is None:
            return True, self._functions
        functions = defaultdict(list)
        for f in self._functions:
            if "stac_collection" in f["inputs"]:
                for c in f["inputs"]["stac_collection"]["options"]:
                    functions[c].append(f)
        return collection in functions, functions[collection]


def get_function_repo() -> ActionCreatorRepository:
    return ActionCreatorRepository(FUNCTIONS)
