from __future__ import annotations

import datetime as dt
from typing import Any

from src.services.ades.token_client import WorkspaceTokenResponse


class FakeTokenClient:
    async def get_token(self, user_id: str = "me"):
        return None, WorkspaceTokenResponse(
            access="token123",
            accessExpiry=dt.datetime.now(),
            refresh="refresh123",
            refreshExpiry=dt.datetime.now(),
            scope="profile workspace:test",
        )


def fake_ws_token_session_auth_client_factory(*args: Any, **kwargs: Any) -> FakeTokenClient:
    return FakeTokenClient()
