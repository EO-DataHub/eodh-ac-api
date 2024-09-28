from __future__ import annotations

import pytest

from src.services.validation_utils import ensure_area_smaller_than
from tests.unit.api.v1_0.schemas.test_functions import TEST_HEATHROW_AOI, TEST_UK_AOI


def test_ensure_area_smaller_than_func_rises_error() -> None:
    with pytest.raises(ValueError, match="Area exceeds 1000 square kilometers"):
        ensure_area_smaller_than(geom=TEST_UK_AOI, area_size_limit=1000)


def test_ensure_area_smaller_than_func_does_not_rais_an_error() -> None:
    ensure_area_smaller_than(geom=TEST_HEATHROW_AOI, area_size_limit=1000)