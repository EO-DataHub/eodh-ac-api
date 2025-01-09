from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from starlette import status

from src.api.v1_3.action_creator.schemas.history import ActionCreatorJobSummary

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from starlette.testclient import TestClient


def test_get_job_submissions_status_endpoint_returns_successful_response(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    test_job_id = str(uuid.uuid4())

    # Act
    response = client.get(
        f"/api/v1.3/action-creator/workflow-submissions/{test_job_id}",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    ActionCreatorJobSummary(**response.json())
