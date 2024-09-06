from __future__ import annotations

import abc
from typing import Any


class AbstractActionCreatorRepository(abc.ABC):
    @abc.abstractmethod
    def get_available_functions(self, collection: str | None = None) -> tuple[bool, list[dict[str, Any]]]: ...
