from __future__ import annotations

import json
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

from pystac import Catalog, Item

DATA_DIR = Path(__file__).parent / "routes" / "data"
STAC_CATALOGS: dict[str, dict[str, list[str]]] = {
    "v1-lcc-glc": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v1-lcc-corine": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v1-lcc-wb": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v1-wq": {"assets": ["doc", "cdom", "ndwi", "cya_cells", "turb"], "assets_to_keep": ["doc", "turb"]},
    "v1-rc-ndvi": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v2-ndvi": {"assets": ["ndvi"], "assets_to_keep": ["ndvi"]},
    "v2-wq": {"assets": ["doc", "cdom", "ndwi", "cya_cells", "turb"], "assets_to_keep": ["cya_cells"]},
    "v2-adv-wq": {"assets": ["doc", "cdom", "ndwi", "cya_cells", "turb"], "assets_to_keep": ["cdom", "ndwi"]},
    "v2-lcc-glc": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v2-lcc-corine": {"assets": ["data"], "assets_to_keep": ["data"]},
    "v2-s2": {"assets": [], "assets_to_keep": []},
}


def load_stac_items(items_fp: Path) -> Generator[Item]:
    yield from [Item.from_dict(i) for i in json.loads(items_fp.read_text(encoding="utf-8"))["features"]]


def load_stac_catalog(catalog_dir: Path) -> Generator[Item]:
    cat = Catalog.from_file(catalog_dir / "catalog.json")
    yield from cat.get_items(recursive=True)


def prepare_stac_client_mock(client_mock: MagicMock, stac_catalog: str) -> None:
    # Mock the Client instance and its search method
    mock_client_instance = MagicMock()
    client_mock.open.return_value = mock_client_instance
    mock_search = MagicMock()
    mock_client_instance.search.return_value = mock_search
    mock_search.items_as_dicts.return_value = [
        j.to_dict() for j in load_stac_catalog(catalog_dir=DATA_DIR / stac_catalog)
    ]
    mock_search.items.return_value = load_stac_catalog(catalog_dir=DATA_DIR / stac_catalog)
