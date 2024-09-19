from __future__ import annotations

from fastapi import APIRouter

health_router_v1_0 = APIRouter(prefix="/health", tags=["Health Check"])


@health_router_v1_0.get("/ping")
async def ping() -> str:
    return "pong"
