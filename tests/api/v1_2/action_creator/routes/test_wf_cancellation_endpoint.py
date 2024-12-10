from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from starlette import status

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from starlette.testclient import TestClient


def test_workflow_cancellation_endpoint_should_return_successful_response(
    client: TestClient,
    auth_token_module_scoped: str,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
) -> None:
    # Arrange
    wf_id = str(uuid.uuid4())

    # Act
    response = client.delete(
        f"/api/v1.2/action-creator/workflow-submissions/{wf_id}",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    )

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
