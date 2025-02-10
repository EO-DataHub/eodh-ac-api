from __future__ import annotations

from typing import Any, NamedTuple

from pydantic import BaseModel, Field

from src.services.stac.schemas import EXAMPLE_FEATURE


class FetchItemResult(NamedTuple):
    collection: str
    items: list[dict[str, Any]]
    token: str | None = None


class SearchContext(BaseModel):
    limit: int
    returned: int


class StacSearchResponse(BaseModel):
    items: dict[str, Any] = Field(..., examples=[{"type": "FeatureCollection", "features": [EXAMPLE_FEATURE]}])
    continuation_tokens: dict[str, str | None] = Field(..., examples=[{"sentinel-2-l2a-ard": "MTcwMDIxOTYxMTAwMA=="}])
    context: SearchContext
