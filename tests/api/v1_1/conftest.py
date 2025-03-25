from __future__ import annotations

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from tests.fakes.ades import FakeADESClient, fake_ades_client_factory


@pytest.fixture
def mocked_ades_factory() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_1.action_creator.routes.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock


@pytest.fixture
def mocked_ades_factory_ws() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_1.action_creator.ws.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock
