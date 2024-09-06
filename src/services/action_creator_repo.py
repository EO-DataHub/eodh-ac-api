from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.services.db import AbstractActionCreatorRepository


class ActionCreatorRepository(AbstractActionCreatorRepository):
    def __init__(self, functions: list[dict[str, Any]]) -> None:
        self._functions = functions

    def get_available_functions(
        self,
        collection: str | None = None,
    ) -> tuple[bool, list[dict[str, Any]]]:
        if collection is None:
            return True, self._functions
        _funcs = defaultdict(list)
        for f in self._functions:
            if "collection" in f["parameters"]:
                for c in f["parameters"]["collection"]["options"]:
                    _funcs[c].append(f)
        return collection in _funcs, _funcs[collection]
