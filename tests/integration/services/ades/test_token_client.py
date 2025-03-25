from __future__ import annotations

from src.core.settings import current_settings
from src.services.ades.token_client import WorkspaceScopedTokenClient, ws_token_session_auth_client_factory
from src.utils.logging import get_logger


async def test_workspace_scoped_token_client(auth_token_func_scoped: str) -> None:
    # Arrange
    settings = current_settings()
    client = WorkspaceScopedTokenClient(
        url=settings.eodh.workspace_services_endpoint,
        workspace=settings.eodh.username,
        token=auth_token_func_scoped,
        logger=get_logger(__name__),
    )

    # Act
    err, response = await client.get_token(user_id="me")

    # Assert
    assert err is None
    assert response is not None


def test_client_factory(auth_token_func_scoped: str) -> None:
    client = ws_token_session_auth_client_factory(token=auth_token_func_scoped, workspace="test")

    assert client is not None
    assert client.token == auth_token_func_scoped
    assert client.workspace == "test"
    assert client.url == current_settings().eodh.workspace_services_endpoint
