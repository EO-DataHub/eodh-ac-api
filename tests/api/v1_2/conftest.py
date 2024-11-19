from __future__ import annotations

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.services.ades.factory import fake_ades_client_factory
from src.services.ades.fake_client import FakeADESClient


@pytest.fixture
def mocked_ades_factory() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_2.action_creator.routes.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock
