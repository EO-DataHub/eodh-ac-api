from __future__ import annotations

import abc
from typing import Any


class AbstractActionCreatorRepository(abc.ABC):
    @abc.abstractmethod
    def get_available_functions(self) -> list[dict[str, Any]]: ...

    @abc.abstractmethod
    def get_available_functions_for_collection(self, collection: str) -> list[dict[str, Any]]: ...
