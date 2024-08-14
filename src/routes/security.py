from __future__ import annotations

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from src.core.settings import current_settings

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: APIKeyHeader = Security(api_key_header)) -> APIKeyHeader:  # noqa: B008
    if api_key == current_settings().api_key:
        return api_key
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")
