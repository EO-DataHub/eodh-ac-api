from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Any

from src.services.ades.token_client import WorkspaceTokenResponse

if TYPE_CHECKING:
    from src.services.ades.base_client import ErrorResponse


class FakeTokenClient:
    async def get_token(self, user_id: str = "me") -> tuple[ErrorResponse | None, WorkspaceTokenResponse | None]:  # noqa: ARG002, PLR6301, RUF100
        return None, WorkspaceTokenResponse(
            access="token123",
            accessExpiry=dt.datetime.now(tz=dt.UTC),
            refresh="refresh123",
            refreshExpiry=dt.datetime.now(tz=dt.UTC),
            scope="profile workspace:test",
        )


def fake_ws_token_session_auth_client_factory(*args: Any, **kwargs: Any) -> FakeTokenClient:  # noqa: ARG001
    return FakeTokenClient()
