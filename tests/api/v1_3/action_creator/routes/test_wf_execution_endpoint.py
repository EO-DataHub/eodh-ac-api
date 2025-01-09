from __future__ import annotations

from operator import itemgetter
from typing import TYPE_CHECKING, Any

import pytest
from starlette import status

from src.api.v1_3.action_creator.schemas.history import ActionCreatorJob
from tests.api.v1_3.conftest import TEST_WORKFLOWS

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "wf_spec",
    TEST_WORKFLOWS.items(),
    ids=itemgetter(0),
)
def test_workflow_execution_endpoint_should_return_expected_response(
    wf_spec: tuple[str, dict[str, Any]],
    client: TestClient,
    auth_token_module_scoped: str,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
) -> None:
    # Arrange
    _, wf = wf_spec

    # Act
    response = client.post(
        "/api/v1.3/action-creator/workflow-submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=wf["value"],
    )

    # Assert
    if wf["should_raise"]:
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"][0]["type"] == wf["error"]
    else:
        assert response.status_code == status.HTTP_202_ACCEPTED
        ActionCreatorJob(**response.json())
