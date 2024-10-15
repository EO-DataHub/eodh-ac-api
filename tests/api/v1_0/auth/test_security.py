from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from starlette import status

if TYPE_CHECKING:
    from starlette.testclient import TestClient


@pytest.mark.parametrize(
    ("method", "endpoint"),
    [
        ("get", "action-creator/functions"),
        ("get", "action-creator/submissions"),
        ("get", "action-creator/submissions/dummy-id"),
        ("post", "action-creator/submissions"),
        ("delete", "action-creator/submissions/dummy-id"),
    ],
    ids=[
        "GET-functions",
        "GET-job-history",
        "GET-job-details",
        "POST-submissions",
        "DELETE-job",
    ],
)
@pytest.mark.parametrize("api_version", ["/api/v1.0"], ids=["v1.0"])
def test_functions_endpoint_returns_forbidden_error_when_no_token_specified(
    api_version: str,
    method: str,
    endpoint: str,
    client: TestClient,
) -> None:
    response = getattr(client, method)(f"{api_version}/{endpoint}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("method", "endpoint"),
    [
        ("get", "action-creator/functions"),
        ("get", "action-creator/submissions"),
        ("get", "action-creator/submissions/dummy-id"),
        ("post", "action-creator/submissions"),
        ("delete", "action-creator/submissions/dummy-id"),
    ],
    ids=[
        "GET-functions",
        "GET-job-history",
        "GET-job-details",
        "POST-submissions",
        "DELETE-job",
    ],
)
@pytest.mark.parametrize("api_version", ["/api/v1.0"], ids=["v1.0"])
def test_functions_endpoint_returns_unauthorized_error_when_bad_token(
    api_version: str,
    method: str,
    endpoint: str,
    client: TestClient,
) -> None:
    response = getattr(client, method)(
        f"{api_version}/{endpoint}",
        headers={"Authorization": "Bearer bad_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
