from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from src.utils.logging import get_logger

_logger = get_logger(__name__)
datasets_router_v1_3 = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)


@datasets_router_v1_3.get("/")
async def get_datasets() -> list[dict[str, Any]]:
    return [
        {
            "id": "sentinel-2-l2a-ard",
            "name": "Sentinel-2 - L2A ARD",
        }
    ]
