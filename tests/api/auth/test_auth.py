from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi import status

from src.core.settings import current_settings

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


@pytest.mark.parametrize("api_version", ["1.2"])
def test_authenticate_success(api_version: str, client: TestClient) -> None:
    settings = current_settings()

    response = client.post(
        f"/api/v{api_version}/auth/token",
        json={"username": settings.eodh.username, "password": settings.eodh.password},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None


@pytest.mark.parametrize("api_version", ["1.2"])
def test_authenticate_failure(api_version: str, client: TestClient) -> None:
    response = client.post(
        f"/api/v{api_version}/auth/token",
        json={"username": "test", "password": "test"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["error_description"] == "Invalid user credentials"


@pytest.mark.parametrize("api_version", ["1.2"])
def test_introspect_success(api_version: str, client: TestClient) -> None:
    settings = current_settings()

    token_response = client.post(
        f"/api/v{api_version}/auth/token",
        json={"username": settings.eodh.username, "password": settings.eodh.password},
    )

    response = client.post(
        f"/api/v{api_version}/auth/token/introspection",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )

    assert response.status_code == status.HTTP_200_OK
    introspect_data = response.json()
    assert introspect_data["preferred_username"] is not None
    assert introspect_data["active"] is True or introspect_data["active"] is None
    assert {
        "exp",
        "iat",
        "jti",
        "iss",
        "aud",
        "sub",
        "typ",
        "azp",
        "session_state",
        "allowed-origins",
        "realm_access",
        "resource_access",
        "scope",
        "sid",
        "email_verified",
        "name",
        "preferred_username",
        "given_name",
        "family_name",
        "email",
        "client_id",
        "username",
        "token_type",
        "active",
    }.difference(introspect_data.keys()) == set()
