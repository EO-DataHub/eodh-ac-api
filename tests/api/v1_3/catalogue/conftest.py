from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from pystac import Catalog, Item

from src.services.stac.client import FakeStacClient

if TYPE_CHECKING:
    from collections.abc import Generator
    from unittest.mock import MagicMock

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


def prepare_stac_client_mock(
    stac_client_factory_mock: MagicMock,
    stac_catalog: str,
    raise_status_code: int | None = None,
    raise_status_msg: str | None = None,
) -> None:
    # Mock the Client instance and its search method
    stac_client_factory_mock.return_value = FakeStacClient(
        processing_results_to_fetch=list(load_stac_catalog(catalog_dir=DATA_DIR / stac_catalog)),
        raise_status_code=raise_status_code,
        raise_status_msg=raise_status_msg,
    )
