from __future__ import annotations

from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["Health Check"])


@health_router.get("/ping")
async def ping() -> str:
    return "pong"
