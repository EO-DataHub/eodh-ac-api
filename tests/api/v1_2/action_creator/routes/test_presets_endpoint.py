from __future__ import annotations

from typing import TYPE_CHECKING

from starlette import status

from src.api.v1_2.action_creator.schemas.presets import PRESETS, PresetList

if TYPE_CHECKING:
    from starlette.testclient import TestClient


def test_presets_endpoint(client: TestClient, auth_token: str) -> None:
    # Act
    response = client.get("/api/v1.2/action-creator/presets", headers={"Authorization": f"Bearer {auth_token}"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = PresetList(**response.json())
    assert result.presets
    assert result.total == len(PRESETS)
