from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.api.v1_0.auth.routes import validate_access_token, validate_access_token_if_provided
from src.api.v1_3.catalogue.schemas.stac_search import (
    StacSearchResponse,
)
from src.api.v1_3.catalogue.schemas.visualization import JobAssetsChartVisualizationResponse, VisualizationRequest
from src.core.settings import current_settings
from src.services.charts.data_builder import ChartDataBuilder
from src.services.stac.client import StacSearchClient, stac_client_factory
from src.services.stac.schemas import (
    EXAMPLE_SEARCH_MODEL,
    EXAMPLE_SEARCH_NEXT_PAGE,
    StacSearch,
)
from src.utils.logging import get_logger

_logger = get_logger(__name__)
catalogue_router_v1_3 = APIRouter(
    prefix="/catalogue",
    tags=["Catalogue"],
)


@catalogue_router_v1_3.post(
    "/stac/catalogs/user-datasets/{workspace}/processing-results/cat_{job_id}/charts",
    response_model=JobAssetsChartVisualizationResponse,
)
async def get_visualization_data_for_job_results(
    workspace: str,
    job_id: str,
    visualization_request: VisualizationRequest,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> dict[str, Any]:
    settings = current_settings()
    client = stac_client_factory()
    builder = ChartDataBuilder()

    items = await client.fetch_processing_results(
        token=credential.credentials,
        job_id=job_id,
        stac_api_endpoint=settings.eodh_stac_api.endpoint,
        workspace=workspace,
        stac_query=visualization_request.stac_query,
    )

    build_result = builder.build(items=items, assets=visualization_request.assets)

    if build_result.success:
        return {"job_id": job_id, "assets": build_result.result}

    raise HTTPException(
        status_code=build_result.error.status_code,  # type: ignore[union-attr]
        detail=build_result.error.detail,  # type: ignore[union-attr]
    )


@catalogue_router_v1_3.post("/stac/search", response_model=StacSearchResponse)
async def stac_search(
    credential: Annotated[HTTPAuthorizationCredentials | None, Depends(validate_access_token_if_provided)],  # noqa: ARG001
    stac_search_query: Annotated[
        dict[str, StacSearch],
        Body(
            openapi_examples={
                "sentinel-1-grd": {
                    "summary": "Query S1 GRD",
                    "description": "S1 GRD search.",
                    "value": {"sentinel-1-grd": EXAMPLE_SEARCH_MODEL["sentinel-1-grd"]},
                },
                "sentinel-2-l2a": {
                    "summary": "Query S2 L2A",
                    "description": "S2 L2A search.",
                    "value": {"sentinel-2-l2a": EXAMPLE_SEARCH_MODEL["sentinel-2-l2a"]},
                },
                "sentinel-2-l2a-ard": {
                    "summary": "Query S2 L2A ARD",
                    "description": "S2 L2A ARD search.",
                    "value": {"sentinel-2-l2a-ard": EXAMPLE_SEARCH_MODEL["sentinel-2-l2a-ard"]},
                },
                "sentinel-2": {
                    "summary": "Query S2 L2A + S2 L1C",
                    "description": "S2 L2A search.",
                    "value": {
                        "sentinel-2-l2a": EXAMPLE_SEARCH_MODEL["sentinel-2-l2a"],
                        "sentinel-2-l1c": EXAMPLE_SEARCH_MODEL["sentinel-2-l1c"],
                    },
                },
                "multi-ds-query": {
                    "summary": "Query S1 GRD + S2 L1C + S2 L2A + S2 ARD",
                    "description": "Multi-dataset search.",
                    "value": EXAMPLE_SEARCH_MODEL,
                },
                "next-page-query": {
                    "summary": "Query S2 ARD - next page",
                    "description": "S2 ARD next page search.",
                    "value": EXAMPLE_SEARCH_NEXT_PAGE,
                },
            },
        ),
    ],
) -> dict[str, Any]:
    client = StacSearchClient()
    return await client.multi_collection_fetch_items(stac_search_query)
