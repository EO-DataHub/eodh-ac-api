from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.api.v1_3.action_creator.schemas.functions import FunctionsResponse
from src.api.v1_3.action_creator.schemas.workflow_tasks import FUNCTIONS

if TYPE_CHECKING:
    from starlette.testclient import TestClient


def test_get_action_creator_functions_happy_path(client: TestClient, auth_token_module_scoped: str) -> None:
    # Act
    response = client.get(
        "/api/v1.3/action-creator/functions", headers={"Authorization": f"Bearer {auth_token_module_scoped}"}
    )

    # Assert
    FunctionsResponse(**response.json())


def test_get_action_creator_functions_returns_empty_result_set_for_bad_dataset(
    client: TestClient, auth_token_module_scoped: str
) -> None:
    # Act
    response = client.get(
        "/api/v1.3/action-creator/functions?dataset=dummy-dataset",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    )

    # Assert
    result = FunctionsResponse(**response.json())
    assert not result.functions
    assert result.total == 0


@pytest.mark.parametrize(
    "dataset",
    [
        "sentinel-1-grd",
        "sentinel-2-l2a",
        "sentinel-2-l2a-ard",
        "esa-lccci-glcm",
        "clms-corine-lc",
        "clms-water-bodies",
    ],
)
def test_get_action_creator_functions_returns_expected_functions_for_dataset(
    dataset: str, client: TestClient, auth_token_module_scoped: str
) -> None:
    # Arrange
    expected_functions = [
        f["identifier"] for f in FUNCTIONS if dataset in f["compatible_input_datasets"] and f["visible"]
    ]

    # Act
    response = client.get(
        f"/api/v1.3/action-creator/functions?dataset={dataset}",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    )

    # Assert
    result = FunctionsResponse(**response.json())
    assert len(result.functions) == len(expected_functions)
    assert result.total == len(expected_functions)
    assert [f.identifier for f in result.functions] == expected_functions
