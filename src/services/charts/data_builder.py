from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from starlette import status

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pystac import Asset, Item

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


class BuildError(BaseModel):
    status_code: int
    detail: str


class BuildResult(BaseModel):
    error: BuildError | None = None
    result: dict[str, dict[str, Any]] = Field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.error is None


class ChartDataBuilderBase(abc.ABC):
    @abc.abstractmethod
    def build(self, items: Iterable[Item], assets: list[str] | None = None) -> BuildResult: ...


class ChartDataBuilder(ChartDataBuilderBase):
    @staticmethod
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

    @staticmethod
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
                        "color-hint": c["color-hint"][:7]
                        if c["color-hint"].startswith("#")
                        else f"#{c['color-hint']}"[:7],
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

    @staticmethod
    def _post_process_stacked_bar_chart_data(asset_data: dict[str, Any]) -> dict[str, Any]:
        x_labels = asset_data["x_labels"]
        records = []
        chart_data: dict[str, Any] = {}

        for cls in asset_data["data"].values():
            chart_data[cls["name"]] = {}
            for datetime, area in zip(x_labels, cls["area"], strict=False):
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

    @staticmethod
    def _post_process_range_area_data(asset_data: dict[str, Any]) -> dict[str, Any]:
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

    def build(self, items: Iterable[Item], assets: list[str] | None = None) -> BuildResult:  # noqa: C901
        assets_dict: dict[str, dict[str, Any]] = {}
        for item in items:
            # Check requested assets are present under the Item
            if assets and (missing_assets := set(assets).difference(item.assets)) != set():
                return BuildResult(
                    error=BuildError(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Assets {missing_assets} not found",
                    )
                )

            for asset_key, asset in item.assets.items():
                # Skip asset if not requested
                if assets and asset_key not in assets:
                    continue

                # Skip asset if not in a data role
                if asset.roles is not None and "data" not in asset.roles:
                    continue

                # Handle range-area chart
                if "statistics" in asset.extra_fields:
                    self._handle_range_area_chart(asset=asset, asset_key=asset_key, assets_dict=assets_dict, item=item)
                    continue

                # Handle stacked bar chart
                if "classification:classes" in asset.extra_fields:
                    self._handle_stacked_bar_chart(asset=asset, asset_key=asset_key, assets_dict=assets_dict, item=item)
                    continue

        # Post process stacked-bar-chart data
        for asset_key, asset_val in assets_dict.items():
            if asset_val["chart_type"] == "classification-stacked-bar-chart":
                assets_dict[asset_key] = self._post_process_stacked_bar_chart_data(asset_val)
            elif asset_val["chart_type"] == "range-area-with-line":
                assets_dict[asset_key] = self._post_process_range_area_data(asset_val)
            else:
                continue

        return BuildResult(result=assets_dict)
