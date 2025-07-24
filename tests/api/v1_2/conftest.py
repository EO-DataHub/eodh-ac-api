from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from tests.fakes.ades import FakeADESClient, fake_ades_client_factory
from tests.fakes.ws_token_client import FakeTokenClient, fake_ws_token_session_auth_client_factory

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mocked_ades_factory() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_2.action_creator.routes.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock


@pytest.fixture
def mocked_ades_factory_ws() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_2.action_creator.ws.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock


@pytest.fixture
def mocked_token_client_factory() -> Generator[MagicMock, None]:
    token_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_2.action_creator.routes.ws_token_session_auth_client_factory",
        fake_ws_token_session_auth_client_factory,
    ) as token_client_factory_mock:
        token_client_factory_mock.return_value = FakeTokenClient
        yield token_client_factory_mock
