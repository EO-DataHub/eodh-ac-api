from __future__ import annotations

from typing import Any

from src.services.db import AbstractActionCreatorRepository


class ActionCreatorRepository(AbstractActionCreatorRepository):
    def __init__(self, functions: list[dict[str, Any]]) -> None:
        self._functions = functions

    def get_available_functions(self) -> list[dict[str, Any]]:
        return self._functions

    def get_available_functions_for_collection(self, collection: str) -> list[dict[str, Any]]:
        return [f for f in self._functions if collection in f["parameters"]["collection"]["options"]]
