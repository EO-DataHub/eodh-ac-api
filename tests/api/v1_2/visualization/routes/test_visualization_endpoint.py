from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from pystac import Catalog, Item
from starlette import status

from src.api.v1_2.visualization.schemas.response import JobAssetsChartVisualizationResponse

if TYPE_CHECKING:
    from httpx import Response
    from starlette.testclient import TestClient

_DATA_DIR = Path(__file__).parent / "data"
_STAC_CATALOGS: dict[str, dict[str, list[str]]] = {
    "v1-lcc-glc": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v1-lcc-corine": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v1-lcc-wb": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v1-wq": {"assets": ["doc", "cdom", "ndwi", "cya_cells", "turb"], "assets_to_keep": ["doc", "turb"]},
    "v1-rc-ndvi": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v2-ndvi": {"assets": ["ndvi"], "assets_to_keep": ["ndvi"]},
    "v2-wq": {"assets": ["doc", "cdom", "ndwi", "cya_cells", "turb"], "assets_to_keep": ["cya_cells"]},
    "v2-adv-wq": {"assets": ["doc", "cdom", "ndwi", "cya_cells", "turb"], "assets_to_keep": ["cdom", "ndwi"]},
    "v2-lcc-glc": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v2-lcc-corine": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v2-s2": {"assets": [], "assets_to_keep": []},
}
_ENDPOINT_TEMPLATE = "/api/v1.2/catalogue/stac/catalogs/user-datasets/{username}/processing-results/cat_{job_id}/search"


def _load_stac_items(catalog_dir: Path) -> Generator[Item]:
    cat = Catalog.from_file(catalog_dir / "catalog.json")
    yield from cat.get_items(recursive=True)


def _prepare_stac_client_mock(client_mock: MagicMock, stac_catalog: str) -> None:
    # Mock the Client instance and its search method
    mock_client_instance = MagicMock()
    client_mock.open.return_value = mock_client_instance
    mock_search = MagicMock()
    mock_client_instance.search.return_value = mock_search
    mock_search.items.return_value = _load_stac_items(catalog_dir=_DATA_DIR / stac_catalog)


def _send_request(
    client: TestClient,
    token: str,
    assets: list[str] | None = None,
    stac_query: dict[str, Any] | None = None,
) -> Response:
    return client.post(
        _ENDPOINT_TEMPLATE.format(username="test", job_id="dummy-job-id"),
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
    response = _send_request(client, token="dummy-token", assets=["test"])  # noqa: S106
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid authentication credentials"}


@patch("src.api.v1_2.visualization.routes.Client")
@pytest.mark.parametrize("stac_catalog", _STAC_CATALOGS)
def test_should_return_200_no_params(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    _prepare_stac_client_mock(client_mock, stac_catalog)

    # Act
    response = _send_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert JobAssetsChartVisualizationResponse(**response.json())


def test_should_return_404_when_catalog_path_does_not_exist(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    response = client.post(
        _ENDPOINT_TEMPLATE.format(username="test", job_id="dummy-job-id"),
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
        "detail": "Catalog cat_dummy-job-id at path user-datasets/test/processing-results not found"
    }


@patch("src.api.v1_2.visualization.routes.Client")
def test_returns_no_data_when_no_assets_to_visualize(
    client_mock: MagicMock,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    _prepare_stac_client_mock(client_mock, "v2-s2")

    # Act
    response = _send_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())
    assert result.assets == {}


@patch("src.api.v1_2.visualization.routes.Client")
@pytest.mark.parametrize("stac_catalog", _STAC_CATALOGS)
def test_returns_404_when_asset_does_not_exist(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    _prepare_stac_client_mock(client_mock, stac_catalog)

    # Act
    response = _send_request(client, token=auth_token_module_scoped, assets=["i-dont-exist"])

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@patch("src.api.v1_2.visualization.routes.Client")
@pytest.mark.parametrize("stac_catalog", _STAC_CATALOGS)
def test_skips_non_data_assets(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    _prepare_stac_client_mock(client_mock, stac_catalog)
    expected_assets = _STAC_CATALOGS[stac_catalog]["assets"]

    # Act
    response = _send_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())
    assert set(result.assets.keys()).difference(expected_assets) == set()


@patch("src.api.v1_2.visualization.routes.Client")
@pytest.mark.parametrize("stac_catalog", _STAC_CATALOGS)
def test_should_keep_only_specified_assets(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    _prepare_stac_client_mock(client_mock, stac_catalog)
    assets_to_keep = _STAC_CATALOGS[stac_catalog]["assets_to_keep"]

    # Act
    response = _send_request(client, token=auth_token_module_scoped, assets=assets_to_keep)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())
    assert set(result.assets.keys()).difference(assets_to_keep) == set()


@patch("src.api.v1_2.visualization.routes.Client")
@pytest.mark.parametrize("stac_catalog", ["v1-rc-ndvi", "v1-wq", "v2-wq", "v2-adv-wq", "v2-ndvi"])
def test_spectral_indices_have_unique_colors(
    client_mock: MagicMock,
    stac_catalog: str,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    _prepare_stac_client_mock(client_mock, stac_catalog)

    # Act
    response = _send_request(client, token=auth_token_module_scoped)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = JobAssetsChartVisualizationResponse(**response.json())

    colors = [asset.color for asset in result.assets.values()]
    assert len(set(colors)) == len(colors)
