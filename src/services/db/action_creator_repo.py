from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.consts.action_creator import FUNCTIONS, PRESETS
from src.services.db.base import AbstractActionCreatorRepository


class ActionCreatorRepository(AbstractActionCreatorRepository):
    def __init__(
        self,
        functions: list[dict[str, Any]],
        presets: list[dict[str, Any]],
    ) -> None:
        self._functions = functions
        self._presets = presets

    @staticmethod
    def _filter_collection(
        items: list[dict[str, Any]],
        collection: str | None = None,
    ) -> tuple[bool, list[dict[str, Any]]]:
        if collection is None:
            return True, items
        _funcs = defaultdict(list)
        for f in items:
            if "stac_collection" in f["inputs"]:
                for c in f["inputs"]["stac_collection"].get("options", []):
                    _funcs[c].append(f)
        return collection in _funcs, _funcs[collection]

    def get_available_functions(
        self,
        collection: str | None = None,
    ) -> tuple[bool, list[dict[str, Any]]]:
        return self._filter_collection(items=self._functions, collection=collection)

    def get_available_presets(
        self,
        collection: str | None = None,
    ) -> tuple[bool, list[dict[str, Any]]]:
        return self._filter_collection(items=self._presets, collection=collection)


def get_function_repo() -> ActionCreatorRepository:
    return ActionCreatorRepository(functions=FUNCTIONS, presets=PRESETS)
