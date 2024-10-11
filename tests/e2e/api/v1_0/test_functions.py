from __future__ import annotations

from typing import TYPE_CHECKING

from starlette import status

if TYPE_CHECKING:
    from starlette.testclient import TestClient


def test_functions_endpoint_returns_forbidden_error_when_no_token_specified(client: TestClient) -> None:
    response = client.get("/api/v1.0/action-creator/functions")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_functions_endpoint_returns_unauthorized_error_when_bad_token(client: TestClient) -> None:
    response = client.get("/api/v1.0/action-creator/functions", headers={"Authorization": "Bearer bad_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_functions_endpoint_returns_all_functions(client: TestClient, auth_token: str) -> None:
    response = client.get("/api/v1.0/action-creator/functions", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["functions"]) > 1


def test_functions_endpoint_returns_functions_for_collection(client: TestClient, auth_token: str) -> None:
    collection = "sentinel-2-l2a"
    response = client.get(
        f"/api/v1.0/action-creator/functions?collection={collection}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    for f in response.json()["functions"]:
        assert collection in f["inputs"]["stac_collection"]["options"]


def test_functions_endpoint_returns_empty_function_list(client: TestClient, auth_token: str) -> None:
    collection = "dummy-collection"
    response = client.get(
        f"/api/v1.0/action-creator/functions?collection={collection}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert not response.json()["functions"]
