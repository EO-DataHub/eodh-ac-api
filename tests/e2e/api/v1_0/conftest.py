from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from app import app as fast_api_app
from src.services.ades.factory import fake_ades_client_factory
from src.services.ades.fake_client import FakeADESClient

if TYPE_CHECKING:
    from fastapi import FastAPI


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return fast_api_app


@pytest.fixture
def mocked_ades_factory() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_0.action_creator.routes.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def raster_calculator_request_body() -> dict[str, Any]:
    return {
        "preset_function": {
            "function_identifier": "raster-calculate",
            "inputs": {
                "aoi": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [14.763294437090849, 50.833598186651244],
                            [15.052268923898112, 50.833598186651244],
                            [15.052268923898112, 50.989077215056824],
                            [14.763294437090849, 50.989077215056824],
                            [14.763294437090849, 50.833598186651244],
                        ]
                    ],
                },
                "date_start": "2024-04-03T00:00:00",
                "date_end": "2024-08-01T00:00:00",
                "index": "NDVI",
                "stac_collection": "sentinel-2-l2a",
            },
        }
    }
