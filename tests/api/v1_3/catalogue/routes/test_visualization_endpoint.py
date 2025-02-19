from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest
from starlette import status

from src.api.v1_3.catalogue.schemas.visualization import JobAssetsChartVisualizationResponse
from tests.api.v1_3.catalogue.conftest import (
    STAC_CATALOGS,
    prepare_stac_client_mock,
)

if TYPE_CHECKING:
    from httpx import Response
    from starlette.testclient import TestClient

_VISUALIZATION_ENDPOINT_TEMPLATE = (
    "/api/v1.3/catalogue/stac/catalogs/user-datasets/{username}/processing-results/cat_{job_id}/charts"
)


def _send_visualization_request(
    client: TestClient,
    token: str,
    assets: list[str] | None = None,
    stac_query: dict[str, Any] | None = None,
) -> Response:
    return client.post(
        url=_VISUALIZATION_ENDPOINT_TEMPLATE.format(username="test", job_id="dummy-job-id"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "assets": assets,
            "stac_query": stac_query,
        },
    )


def test_should_return_401_when_invalid_user_credentials(client: TestClient) -> None:
    response = _send_visualization_request(client, token="dummy-token", assets=["test"])  # noqa: S106
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid authentication credentials"}


@patch("src.services.stac.client.Client")
@pytest.mark.parametrize("stac_catalog", STAC_CATALOGS)
def test_should_return_200_no_params(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    prepare_stac_client_mock(client_mock, stac_catalog)

    # Act
    response = _send_visualization_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert JobAssetsChartVisualizationResponse(**response.json())


def test_should_return_404_when_catalog_path_does_not_exist(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    response = client.post(
        _VISUALIZATION_ENDPOINT_TEMPLATE.format(username="test", job_id="dummy-job-id"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {auth_token_module_scoped}",
        },
        json={
            "assets": ["test"],
            "stac_query": None,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": {
            "code": "NotFoundError",
            "description": "Catalog cat_dummy-job-id not found",
        }
    }


@patch("src.services.stac.client.Client")
def test_returns_no_data_when_no_assets_to_visualize(
    client_mock: MagicMock,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    prepare_stac_client_mock(client_mock, "v2-s2")

    # Act
    response = _send_visualization_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())
    assert result.assets == {}


@patch("src.services.stac.client.Client")
@pytest.mark.parametrize("stac_catalog", STAC_CATALOGS)
def test_returns_404_when_asset_does_not_exist(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    prepare_stac_client_mock(client_mock, stac_catalog)

    # Act
    response = _send_visualization_request(client, token=auth_token_module_scoped, assets=["i-dont-exist"])

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@patch("src.services.stac.client.Client")
@pytest.mark.parametrize("stac_catalog", STAC_CATALOGS)
def test_skips_non_data_assets(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    prepare_stac_client_mock(client_mock, stac_catalog)
    expected_assets = STAC_CATALOGS[stac_catalog]["assets"]

    # Act
    response = _send_visualization_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())
    assert set(result.assets.keys()).difference(expected_assets) == set()


@patch("src.services.stac.client.Client")
@pytest.mark.parametrize("stac_catalog", STAC_CATALOGS)
def test_should_keep_only_specified_assets(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    prepare_stac_client_mock(client_mock, stac_catalog)
    assets_to_keep = STAC_CATALOGS[stac_catalog]["assets_to_keep"]

    # Act
    response = _send_visualization_request(client, token=auth_token_module_scoped, assets=assets_to_keep)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())
    assert set(result.assets.keys()).difference(assets_to_keep) == set()


@patch("src.services.stac.client.Client")
@pytest.mark.parametrize("stac_catalog", ["v1-rc-ndvi", "v1-wq", "v2-wq", "v2-adv-wq", "v2-ndvi"])
def test_spectral_indices_have_unique_colors(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    expected_color_hint_len = 7  # hash symbol + hex RGB color value
    prepare_stac_client_mock(client_mock, stac_catalog)

    # Act
    response = _send_visualization_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())

    colors = [asset.color for asset in result.assets.values()]
    assert len(set(colors)) == len(colors)
    assert all(len(c) == expected_color_hint_len for c in colors)
