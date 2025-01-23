from __future__ import annotations

from typing import TYPE_CHECKING, Any

from starlette import status

from src.api.v1_3.catalogue.routes import SUPPORTED_DATASETS

if TYPE_CHECKING:
    from httpx import Response
    from starlette.testclient import TestClient

_SEARCH_ENDPOINT_PATH = "/api/v1.3/catalogue/stac/search"


def _send_search_request(
    client: TestClient,
    token: str,
    stac_query: dict[str, Any] | None = None,
) -> Response:
    return client.post(
        url=_SEARCH_ENDPOINT_PATH,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json=stac_query,
    )


def test_should_return_401_when_invalid_user_credentials(client: TestClient) -> None:
    # Act
    response = _send_search_request(client, token="dummy-token")  # noqa: S106

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_should_return_404_when_collection_is_not_found(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Act
    response = _send_search_request(
        client, token=auth_token_module_scoped, stac_query={"collections": ["dummy-collection"]}
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"Collections: ['dummy-collection'] are not supported. "
        f"Supported collections: {', '.join(SUPPORTED_DATASETS)}"
    }


def test_should_return_limited_results(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    pass


def test_should_merge_results_from_multiple_datasets(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    pass
