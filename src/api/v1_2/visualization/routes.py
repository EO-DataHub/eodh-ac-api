from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pystac_client import Client
from starlette import status

from src.api.v1_0.auth.routes import validate_access_token
from src.api.v1_2.visualization.schemas import JobAssetsChartVisualizationResponse, VisualizationRequest
from src.core.settings import current_settings
from src.utils.logging import get_logger

_logger = get_logger(__name__)

visualization_router_v1_2 = APIRouter(
    prefix="/catalogue",
    tags=["Visualization"],
)


@visualization_router_v1_2.post(
    "/stac/catalogs/user-datasets/{workspace}/processing-results/cat_{job_id}/search",
    response_model=JobAssetsChartVisualizationResponse,
)
async def get_visualization_data_for_job_results(  # noqa: C901
    workspace: str,
    job_id: str,
    visualization_request: VisualizationRequest,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> dict[str, Any]:
    settings = current_settings()
    stac_client = Client.open(
        f"{settings.eodh_stac_api.endpoint}/catalogs/user-datasets/{workspace}/processing-results/cat_{job_id}",
        headers={"Authorization": f"Bearer {credential.credentials}"},
    )

    search_params = visualization_request.stac_query or {}
    search_params["fields"] = {"include": ["properties.lulc_classes_percentage", "properties.lulc_classes_m2"]}

    items = list(stac_client.search(**search_params).items())

    assets_dict: dict[str, dict[str, Any]] = {}
    for item in items:
        if (
            visualization_request.assets
            and (missing_assets := set(visualization_request.assets).difference(item.assets)) != set()
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assets {missing_assets} not found under catalog {job_id}",
            )

        for asset_key, asset in item.assets.items():
            # Skip asset if not requested
            if visualization_request.assets and asset_key not in visualization_request.assets:
                continue

            # Skip asset if not in a data role
            if asset.roles is not None and "data" not in asset.roles:
                continue

            # Handle range-area chart
            if "statistics" in asset.extra_fields:
                if asset_key not in assets_dict:
                    assets_dict[asset_key] = {
                        "title": asset.title,
                        "chart_type": "range-area-with-line",
                        "data": [],
                        "units": asset.extra_fields["colormap"]["units"],
                        "colors": {  # TODO
                            "line": "000000",
                            "range_area": "5f5f5f",
                        },
                    }
                assets_dict[asset_key]["data"].append({
                    "min": asset.extra_fields["statistics"]["minimum"],
                    "max": asset.extra_fields["statistics"]["maximum"],
                    "median": asset.extra_fields["statistics"]["median"],
                    "x_label": item.datetime,
                })
                continue

            # Handle stacked bar chart
            if "classification:classes" in asset.extra_fields:
                if asset_key not in assets_dict:
                    assets_dict[asset_key] = {
                        "title": asset.title,
                        "chart_type": "classification-stacked-bar-chart",
                        "data": {
                            c["description"]: {
                                "name": c["description"],
                                "area": [],
                                "percentage": [],
                                "color-hint": c["color-hint"],
                            }
                            for c in asset.extra_fields["classification:classes"]
                        },
                        "units": "sq km",
                        "x_labels": [],
                    }
                assets_dict[asset_key]["x_labels"].append(item.datetime)
                for class_meta in asset.extra_fields["classification:classes"]:
                    assets_dict[asset_key]["data"][class_meta["description"]]["area"].append(
                        class_meta.get("area_km2", None)
                        or item.properties["lulc_classes_m2"][str(class_meta["value"])] / 1e6
                    )
                    assets_dict[asset_key]["data"][class_meta["description"]]["percentage"].append(
                        class_meta.get("percentage", None)
                        or item.properties["lulc_classes_percentage"][str(class_meta["value"])]
                    )
                continue

    for asset_key, asset_val in assets_dict.items():
        if asset_val["chart_type"] != "classification-stacked-bar-chart":
            continue
        assets_dict[asset_key]["data"] = list(asset_val["data"].values())

    return {"job_id": job_id, "assets": assets_dict}
