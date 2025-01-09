from __future__ import annotations

from operator import itemgetter
from typing import TYPE_CHECKING, Any

import pytest
from starlette import status

from src.api.v1_3.action_creator.schemas.workflow_tasks import WorkflowValidationResult
from tests.api.v1_3.conftest import TEST_WORKFLOWS

if TYPE_CHECKING:
    from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "wf_spec",
    TEST_WORKFLOWS.items(),
    ids=itemgetter(0),
)
def test_wf_validation_endpoint(
    wf_spec: tuple[str, dict[str, Any]], client: TestClient, auth_token_module_scoped: str
) -> None:
    # Arrange
    _, wf = wf_spec

    # Act
    response = client.post(
        "/api/v1.3/action-creator/workflow-validation",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        json=wf["value"],
    )

    # Assert
    if wf["should_raise"]:
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"][0]["type"] == wf["error"]
    else:
        assert response.status_code == status.HTTP_200_OK
        WorkflowValidationResult(**response.json())
