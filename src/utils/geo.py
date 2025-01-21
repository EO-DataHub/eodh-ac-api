from __future__ import annotations

from typing import Any

import geopandas as gpd
import pyproj
import shapely


def calculate_geodesic_area(polygon: shapely.Polygon) -> float:
    # Define the WGS 84 ellipsoid
    geod = pyproj.Geod(ellps="WGS84")

    # Get the coordinates of the polygon
    lon, lat = polygon.exterior.coords.xy

    # Calculate the geodesic area using pyproj's Geod function
    area, _ = geod.polygon_area_perimeter(lon, lat)

    # Return the area in square meters (area will be negative, so we take the absolute value)
    return float(abs(area))


def chip_aoi(aoi_polygon: shapely.Polygon, chip_size_deg: float = 0.2) -> list[dict[str, Any]]:
    chips = generate_chips(aoi_polygon, chip_size_deg=chip_size_deg)
    return [chip["geometry"] for chip in chips.to_geo_dict()["features"]]


def generate_chips(aoi_geom: shapely.Polygon, chip_size_deg: float = 0.2) -> gpd.GeoDataFrame:
    """Tile the given AOI into smaller tiles of a fixed size in degrees."""
    # Get bounds of AOI
    minx, miny, maxx, maxy = aoi_geom.bounds

    # Create grid of tiles
    tiles = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            tile = shapely.box(x, y, x + chip_size_deg, y + chip_size_deg)
            intersection = tile.intersection(aoi_geom)
            if not intersection.is_empty:
                if isinstance(intersection, shapely.geometry.Polygon):
                    tiles.append(intersection)
                if isinstance(intersection, shapely.geometry.MultiPolygon):
                    tiles.extend(intersection.geoms)
            y += chip_size_deg
        x += chip_size_deg

    # Create GeoDataFrame for tiles
    return gpd.GeoDataFrame(geometry=tiles, crs="EPSG:4326")
