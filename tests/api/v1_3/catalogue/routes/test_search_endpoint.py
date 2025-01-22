from __future__ import annotations

from typing import TYPE_CHECKING, Any

from starlette import status

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
    response = _send_search_request(client, token="dummy-token")  # noqa: S106
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid authentication credentials"}
