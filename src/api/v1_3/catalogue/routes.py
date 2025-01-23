from __future__ import annotations

import asyncio
import json
from typing import Annotated, Any, TypedDict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pystac import Asset, Item
from pystac_client import Client
from pystac_client.exceptions import APIError
from stac_pydantic.api.extensions.sort import SortDirections, SortExtension
from starlette import status

from src.api.v1_0.auth.routes import validate_access_token
from src.api.v1_3.catalogue.schemas.stac_search import (
    FieldsExtension,
    StacSearch,
)
from src.api.v1_3.catalogue.schemas.visualization import JobAssetsChartVisualizationResponse, VisualizationRequest
from src.core.settings import current_settings
from src.utils.logging import get_logger

_logger = get_logger(__name__)


class DatasetLookupRecord(TypedDict):
    catalog_path: str
    collection_name: str


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

DATASET_LOOKUP: dict[str, DatasetLookupRecord] = {
    "sentinel-1-grd": DatasetLookupRecord(
        catalog_path="supported-datasets/earth-search-aws",
        collection_name="sentinel-1-grd",
    ),
    "sentinel-2-l1c": DatasetLookupRecord(
        catalog_path="supported-datasets/earth-search-aws",
        collection_name="sentinel-2-l1c",
    ),
    "sentinel-2-l2a": DatasetLookupRecord(
        catalog_path="supported-datasets/earth-search-aws",
        collection_name="sentinel-2-l2a",
    ),
    "sentinel-2-l2a-ard": DatasetLookupRecord(
        catalog_path="supported-datasets/ceda-stac-catalogue",
        collection_name="sentinel2_ard",
    ),
}

SUPPORTED_DATASETS = set(DATASET_LOOKUP.keys())

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
async def get_visualization_data_for_job_results(  # noqa: C901, PLR0912
    workspace: str,
    job_id: str,
    visualization_request: VisualizationRequest,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> dict[str, Any]:
    settings = current_settings()

    # Connect to STAC catalog
    try:
        stac_client = Client.open(
            f"{settings.eodh_stac_api.endpoint}/catalogs/user-datasets/{workspace}/processing-results/cat_{job_id}",
            headers={"Authorization": f"Bearer {credential.credentials}"},
        )
    except APIError as ex:
        # User not authorized to access this resource or catalog does not exist
        raise HTTPException(
            status_code=ex.status_code,
            detail=json.loads(str(ex)),
        ) from APIError

    # Sanitize params
    search_params = visualization_request.stac_query or StacSearch()
    if search_params.fields is None:
        search_params.fields = FieldsExtension(include=set())

    if search_params.fields.include is None:
        search_params.fields.include = set()

    search_params.fields.include = search_params.fields.include.union({
        "properties.lulc_classes_percentage",
        "properties.lulc_classes_m2",
    })

    if search_params.sortby is None:
        search_params.sortby = [SortExtension(field="properties.datetime", direction=SortDirections.asc)]

    # Perform STAC search
    search = stac_client.search(
        limit=search_params.limit,
        ids=search_params.ids,
        collections=search_params.collections,
        bbox=search_params.bbox,
        intersects=search_params.intersects,
        datetime=search_params.datetime,
        query=search_params.query,
        filter=search_params.filter,
        filter_lang=search_params.filter_lang,
        sortby=[s.model_dump(mode="json") for s in search_params.sortby],
        fields=search_params.fields.model_dump(mode="json"),
    )

    assets_dict: dict[str, dict[str, Any]] = {}
    for item in search.items():
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

    # Classes dict to list
    for asset_key, asset_val in assets_dict.items():
        if asset_val["chart_type"] != "classification-stacked-bar-chart":
            continue
        assets_dict[asset_key]["data"] = list(asset_val["data"].values())

    return {"job_id": job_id, "assets": assets_dict}


@catalogue_router_v1_3.post("/stac/search")
async def stac_search(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
    stac_search_query: dict[str, StacSearch],
) -> dict[str, Any]:
    if diff := set(stac_search_query.keys()).difference(SUPPORTED_DATASETS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collections: {list(diff)} are not supported. "
            f"Supported collections: {', '.join(SUPPORTED_DATASETS)}",
        )

    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, fetch_items, collection, search_params)
        for collection, search_params in stac_search_query.items()
    ]

    # Gather results from all endpoints
    _logger.debug("Gathering items from STAC endpoints...")
    results = await asyncio.gather(*tasks)

    # Flatten the item lists
    all_items: list[dict[str, Any]] = []
    for items in results:
        all_items.extend(items)

    # Sort items by datetime property if present
    # We'll skip items without a valid datetime to avoid errors
    all_items.sort(key=lambda x: x["properties"].get("datetime", ""), reverse=True)

    return {"type": "FeatureCollection", "features": all_items}


def fetch_items(collection: str, search_params: StacSearch) -> list[dict[str, Any]]:
    settings = current_settings()
    lookup = DATASET_LOOKUP[collection]
    stac_client = Client.open(f"{settings.eodh_stac_api.endpoint}/catalogs/{lookup['catalog_path']}")

    if search_params.fields is None:
        search_params.fields = FieldsExtension(include=set())

    if search_params.fields.include is None:
        search_params.fields.include = set()

    search_params.fields.include = search_params.fields.include.union({
        "properties.lulc_classes_percentage",
        "properties.lulc_classes_m2",
    })

    if search_params.sortby is None:
        search_params.sortby = [SortExtension(field="properties.datetime", direction=SortDirections.asc)]

    # Perform STAC search
    search = stac_client.search(
        limit=search_params.limit,
        collections=[lookup["collection_name"]],
        intersects=search_params.intersects,
        datetime=search_params.datetime,
        query=search_params.query,
        filter=search_params.filter,
        filter_lang=search_params.filter_lang,
        sortby=[s.model_dump(mode="json") for s in search_params.sortby],
        fields=search_params.fields.model_dump(mode="json"),
    )
    items = []
    for i, item in enumerate(search.items_as_dicts()):
        if i >= search_params.limit:
            break
        items.append(item)

    return items
