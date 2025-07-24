from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.core.settings import current_settings
from src.services.ades.base_client import APIClient, ErrorResponse
from src.utils.logging import get_logger

if TYPE_CHECKING:
    import datetime as dt
    from logging import Logger


class WorkspaceTokenResponse(BaseModel):
    access: str
    access_expiry: dt.datetime = Field(alias="accessExpiry")
    refresh: str
    refresh_expiry: dt.datetime = Field(alias="refreshExpiry")
    scope: str

    @property
    def scope_list(self) -> list[str]:
        return self.scope.split()


class WorkspaceScopedTokenClient(APIClient):
    def __init__(self, url: str, workspace: str, token: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.token = token
        self.workspace = workspace
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    async def get_token(self, user_id: str = "me") -> tuple[ErrorResponse | None, WorkspaceTokenResponse | None]:
        client_session, retry_client = self._get_retry_client()
        try:
            async with retry_client.post(
                url=f"{self.url}/{self.workspace}/{user_id}/sessions",
                headers=self.headers,
            ) as response:
                if err := await self._handle_common_errors_if_necessary(response):
                    return err, None

                return None, WorkspaceTokenResponse(**(await response.json()))
        finally:
            await client_session.close()


def ws_token_session_auth_client_factory(token: str, workspace: str) -> WorkspaceScopedTokenClient:
    settings = current_settings()
    return WorkspaceScopedTokenClient(
        url=settings.eodh.workspace_services_endpoint,
        workspace=workspace,
        token=token,
        logger=get_logger(__name__),
    )
