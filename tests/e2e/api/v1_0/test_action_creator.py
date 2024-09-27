from __future__ import annotations

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import app

client = TestClient(app)


@pytest.mark.asyncio(scope="function")
async def test_get_job_submissions_endpoint_returns_forbidden_error_when_no_token_specified() -> None:
    response = client.get("/api/v1.0/action-creator/submissions")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio(scope="function")
async def test_get_job_submissions_endpoint_returns_unauthorized_error_when_bad_token() -> None:
    response = client.get("/api/v1.0/action-creator/submissions", headers={"Authorization": "Bearer bad_token"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(scope="function")
async def test_get_job_submissions_endpoint_returns_valid_response_when_all_is_ok(auth_token: str) -> None:
    response = client.get("/api/v1.0/action-creator/submissions", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert all(k in response.json() for k in ("submitted_jobs", "total"))
