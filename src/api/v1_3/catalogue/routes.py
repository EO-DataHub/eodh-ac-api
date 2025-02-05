from __future__ import annotations

from typing import Annotated, Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pystac import Asset, Item
from starlette import status

from src.api.v1_0.auth.routes import validate_access_token
from src.api.v1_3.catalogue.schemas.stac_search import (
    StacSearchResponse,
)
from src.api.v1_3.catalogue.schemas.visualization import JobAssetsChartVisualizationResponse, VisualizationRequest
from src.core.settings import current_settings
from src.services.stac.client import StacSearchClient
from src.services.stac.schemas import (
    EXAMPLE_SEARCH_MODEL,
    EXAMPLE_SEARCH_NEXT_PAGE,
    StacSearch,
)
from src.utils.logging import get_logger

_logger = get_logger(__name__)

COLOR_WHEEL = {
    "ndvi": "#008000",
    "evi": "#15b01a",
    "savi": "#9acd32",
    "data": "#d4526e",
    "doc": "#13eac9",
    "cdom": "#7bc8f6",
    "cya_cells": "#00008b",
    "cya_mg": "#da70d6",
    "chl_a_coastal": "#ffa500",
    "chl_a_low": "#f97306",
    "chl_a_high": "#daa520",
    "ndwi": "#9a0eea",
    "turb": "#6e750e",
    "unknown": "#000000",
}

catalogue_router_v1_3 = APIRouter(
    prefix="/catalogue",
    tags=["Catalogue"],
)


def _handle_range_area_chart(asset: Asset, asset_key: str, assets_dict: dict[str, Any], item: Item) -> None:
    if asset_key not in assets_dict:
        assets_dict[asset_key] = {
            "title": asset.title,
            "chart_type": "range-area-with-line",
            "data": [],
            "units": asset.extra_fields["colormap"]["units"],
            "color": COLOR_WHEEL.get(asset_key, COLOR_WHEEL["unknown"]),
        }
    assets_dict[asset_key]["data"].append({
        "min": asset.extra_fields["statistics"]["minimum"],
        "max": asset.extra_fields["statistics"]["maximum"],
        "median": asset.extra_fields["statistics"]["median"],
        "x_label": item.datetime,
    })


def _handle_stacked_bar_chart(asset: Asset, asset_key: str, assets_dict: dict[str, Any], item: Item) -> None:
    if asset_key not in assets_dict:
        assets_dict[asset_key] = {
            "title": asset.title or "Land cover change",
            "chart_type": "classification-stacked-bar-chart",
            "data": {
                c["description"]: {
                    "name": c["description"],
                    "area": [],
                    "percentage": [],
                    "color-hint": c["color-hint"][:7] if c["color-hint"].startswith("#") else f"#{c['color-hint']}"[:7],
                }
                for c in asset.extra_fields["classification:classes"]
            },
            "units": "sq km",
            "x_labels": [],
        }
    assets_dict[asset_key]["x_labels"].append(item.datetime)
    for class_meta in asset.extra_fields["classification:classes"]:
        area = class_meta.get("area_km2", None)
        if area is None:
            area = item.properties["lulc_classes_m2"][str(class_meta["value"])] / 1e6
        assets_dict[asset_key]["data"][class_meta["description"]]["area"].append(area)

        percentage = class_meta.get("percentage", None)
        if percentage is None:
            percentage = item.properties["lulc_classes_percentage"][str(class_meta["value"])]
        assets_dict[asset_key]["data"][class_meta["description"]]["percentage"].append(percentage)


@catalogue_router_v1_3.post(
    "/stac/catalogs/user-datasets/{workspace}/processing-results/cat_{job_id}/charts",
    response_model=JobAssetsChartVisualizationResponse,
)
async def get_visualization_data_for_job_results(  # noqa: C901
    workspace: str,
    job_id: str,
    visualization_request: VisualizationRequest,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> dict[str, Any]:
    settings = current_settings()
    client = StacSearchClient()

    items = await client.fetch_processing_results(
        token=credential.credentials,
        job_id=job_id,
        stac_api_endpoint=settings.eodh_stac_api.endpoint,
        workspace=workspace,
        stac_query=visualization_request.stac_query,
    )

    assets_dict: dict[str, dict[str, Any]] = {}
    for item in items:
        # Check requested assets are present under the Item
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
                _handle_range_area_chart(asset=asset, asset_key=asset_key, assets_dict=assets_dict, item=item)
                continue

            # Handle stacked bar chart
            if "classification:classes" in asset.extra_fields:
                _handle_stacked_bar_chart(asset=asset, asset_key=asset_key, assets_dict=assets_dict, item=item)
                continue

    # Post process stacked-bar-chart data
    for asset_key, asset_val in assets_dict.items():
        if asset_val["chart_type"] == "classification-stacked-bar-chart":
            assets_dict[asset_key] = post_process_stacked_bar_chart_data(asset_val)
        elif asset_val["chart_type"] == "range-area-with-line":
            assets_dict[asset_key] = post_process_range_area_data(asset_val)
        else:
            continue

    return {"job_id": job_id, "assets": assets_dict}


def post_process_stacked_bar_chart_data(asset_data: dict[str, Any]) -> dict[str, Any]:
    x_labels = asset_data["x_labels"]
    records = []
    chart_data: dict[str, Any] = {}

    for cls in asset_data["data"].values():
        chart_data[cls["name"]] = {}
        for datetime, area in zip(x_labels, cls["area"]):
            records.append({
                "name": cls["name"],
                "area": area,
                "color-hint": cls["color-hint"],
                "datetime": datetime,
            })

    records_df = pd.DataFrame(records)
    results = records_df.groupby(["datetime", "name", "color-hint"]).sum().reset_index()
    sum_per_dt = records_df[["datetime", "area"]].groupby("datetime").sum()
    x_labels = []

    for _, row in results.iterrows():
        cls_name = row["name"]

        if row["datetime"] not in x_labels:
            x_labels.append(row["datetime"])

        if "area" not in chart_data[cls_name]:
            chart_data[cls_name]["name"] = cls_name
            chart_data[cls_name]["color-hint"] = row["color-hint"]
            chart_data[cls_name]["area"] = [row["area"]]
            chart_data[cls_name]["percentage"] = [
                row["area"] / sum_per_dt.loc[row["datetime"]]["area"].item() * 100
                if sum_per_dt.loc[row["datetime"]]["area"].item() != 0
                else 0
            ]
            continue

        chart_data[cls_name]["area"].append(row["area"])
        chart_data[cls_name]["percentage"].append(
            row["area"] / sum_per_dt.loc[row["datetime"]]["area"].item() * 100
            if sum_per_dt.loc[row["datetime"]]["area"].item() != 0
            else 0
        )

    asset_data["data"] = list(chart_data.values())
    asset_data["x_labels"] = x_labels

    return asset_data


def post_process_range_area_data(asset_data: dict[str, Any]) -> dict[str, Any]:
    asset_frame = pd.DataFrame(asset_data["data"])
    results = []
    for dt, frame in asset_frame.groupby("x_label"):
        min_ = np.nanmin(frame["min"].fillna(np.nan)).item()
        max_ = np.nanmax(frame["max"].fillna(np.nan)).item()
        median = np.nanmean(frame["median"].fillna(np.nan)).item()
        results.append({
            "x_label": dt,
            "min": min_ if not np.isnan(min_) else None,
            "max": max_ if not np.isnan(max_) else None,
            "median": median if not np.isnan(median) else None,
        })
    asset_data["data"] = results
    return asset_data


@catalogue_router_v1_3.post("/stac/search", response_model=StacSearchResponse)
async def stac_search(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
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
