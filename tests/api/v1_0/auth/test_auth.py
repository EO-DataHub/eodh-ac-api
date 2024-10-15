from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import status

from src.core.settings import current_settings

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_authenticate_success(client: TestClient) -> None:
    settings = current_settings()

    response = client.post(
        "/api/v1.0/auth/token",
        json={"username": settings.eodh_auth.username, "password": settings.eodh_auth.password},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None


def test_authenticate_failure(client: TestClient) -> None:
    response = client.post(
        "/api/v1.0/auth/token",
        json={"username": "test", "password": "test"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["error_description"] == "Invalid user credentials"


def test_introspect_success(client: TestClient) -> None:
    settings = current_settings()

    token_response = client.post(
        "/api/v1.0/auth/token",
        json={"username": settings.eodh_auth.username, "password": settings.eodh_auth.password},
    )

    response = client.post(
        "/api/v1.0/auth/token/introspection",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )

    assert response.status_code == status.HTTP_200_OK
    introspect_data = response.json()
    assert introspect_data["username"] is not None
    assert introspect_data["active"]
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
