from __future__ import annotations

from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from src.services.ades.factory import fake_ades_client_factory
from src.services.ades.fake_client import FakeADESClient


@pytest.fixture
def mocked_ades_factory() -> Generator[MagicMock]:
    ades_client_factory_mock: MagicMock
    with patch(  # type: ignore[assignment]
        "src.api.v1_0.action_creator.routes.ades_client_factory",
        fake_ades_client_factory,
    ) as ades_client_factory_mock:
        ades_client_factory_mock.return_value = FakeADESClient
        yield ades_client_factory_mock


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
                "stac_collection": "sentinel-2-l2a",
            },
            "parameters": {
                "limit": 10,
                "index": "NDVI",
            },
        }
    }


@pytest.fixture
def lulc_change_request_body() -> dict[str, Any]:
    return {
        "preset_function": {
            "function_identifier": "lulc-change",
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
                "stac_collection": "esacci-globallc",
            },
        }
    }


@pytest.fixture
def water_quality_request_body() -> dict[str, Any]:
    return {
        "preset_function": {
            "function_identifier": "water-quality",
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
                "stac_collection": "sentinel-2-l2a",
            },
            "parameters": {
                "calibrate": True,
                "index": "CYA",
            },
        }
    }
