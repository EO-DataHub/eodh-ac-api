from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from geojson_pydantic import Polygon

from src.api.v1_0.action_creator.schemas import RasterCalculatorFunctionInputs, RasterCalculatorIndex

TEST_BBOX = [
    14.763294437090849,  # xmin,
    50.833598186651244,  # ymin,
    15.052268923898112,  # xmax,
    50.989077215056824,  # ymax,
]
TEST_HEATHROW_AOI = {
    "type": "Polygon",
    "coordinates": [
        [
            [-0.511790994620525, 51.445639911633833],
            [-0.511790994620525, 51.496989653093614],
            [-0.408954489023431, 51.496989653093614],
            [-0.408954489023431, 51.445639911633833],
            [-0.511790994620525, 51.445639911633833],
        ]
    ],
}
TEST_UK_AOI = {
    "type": "Polygon",
    "coordinates": [
        [
            [-1.223466311375788, 61.31719334443931],
            [1.370284636635369, 61.325674412273941],
            [-0.725262397734842, 59.368017527839186],
            [-2.471551593043348, 58.140279283605295],
            [-1.035713810234129, 57.374284117260167],
            [-1.501390928983066, 56.442087505023629],
            [-0.958100957109309, 55.596237835576162],
            [0.012059706950972, 54.754153136171517],
            [1.680736049134656, 53.434319356981348],
            [2.728509566319762, 52.428548962213881],
            [2.573283860070116, 51.544328677523261],
            [1.4867039163226, 50.961418953205722],
            [0.55534967882473, 50.420579711791675],
            [-1.850648768044769, 50.147818892201784],
            [-3.674550816478098, 50.023319659449776],
            [-5.808904277410717, 49.471676501661747],
            [-6.817871368033412, 49.547270117170164],
            [-6.313387822722064, 50.765471471431248],
            [-6.158162116472418, 51.423498298599625],
            [-8.176096297717805, 51.399293794268331],
            [-10.543288318024894, 51.034687034050158],
            [-11.047771863336241, 51.928836992058727],
            [-11.280610422710705, 52.875841774515031],
            [-10.737320450836949, 54.281128923640573],
            [-9.728353360214253, 55.618158162630699],
            [-8.447741283654686, 56.291630857320015],
            [-8.952224828966031, 57.290498835907826],
            [-9.417901947714967, 57.790351349666814],
            [-8.408934857092273, 58.950242804416348],
            [-7.244742060219933, 59.328449034626686],
            [-5.110388599287317, 59.858745908936505],
            [-3.829776522727744, 60.188362449299973],
            [-2.19990660710647, 60.913337458441163],
            [-1.656616635232713, 61.138915364882514],
            [-1.223466311375788, 61.31719334443931],
        ]
    ],
}


def test_raster_calculate_preset_validation_neither_aoi_nor_bbox_provided() -> None:
    data = {
        "aoi": None,
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="At least one of AOI or BBOX must be provided"):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_aoi_too_big() -> None:
    # Arrange
    data = {
        "aoi": TEST_UK_AOI,
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Area exceeds"):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_raises_if_both_aoi_and_bbox_provided() -> None:
    data = {
        "aoi": TEST_HEATHROW_AOI,
        "bbox": TEST_BBOX,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="AOI and BBOX are mutually exclusive, provide only one of them."):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_uses_bbox_if_no_aoi() -> None:
    # Arrange
    data = {
        "aoi": None,
        "bbox": TEST_BBOX,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data)

    # Assert
    assert result.aoi is not None
    assert result.aoi == Polygon.from_bounds(*TEST_BBOX)


def test_raster_calculate_preset_validation_parse_geojson() -> None:
    # Arrange
    data = {
        "aoi": json.dumps(TEST_HEATHROW_AOI),
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data)

    # Assert
    assert result.aoi is not None
    assert result.aoi == Polygon(**TEST_HEATHROW_AOI)


def test_raster_calculate_preset_validation_raises_for_unsupported_collection() -> None:
    data = {
        "aoi": TEST_HEATHROW_AOI,
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "test",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Collection 'test' cannot be used"):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_raises_for_invalid_date_range() -> None:
    data = {
        "aoi": TEST_HEATHROW_AOI,
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2023-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="End date cannot be before start date."):
        RasterCalculatorFunctionInputs(**data)


def test_raster_calculate_preset_validation_uses_ndvi_if_index_not_provided() -> None:
    data = {
        "aoi": TEST_HEATHROW_AOI,
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data)

    # Assert
    assert result.index == RasterCalculatorIndex.NDVI


def test_raster_calculate_preset_validation_happy_path() -> None:
    data = {
        "aoi": TEST_HEATHROW_AOI,
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data)

    # Assert
    assert result.aoi == Polygon(**TEST_HEATHROW_AOI)
    assert result.bbox is None
    assert result.date_start == datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert result.date_end == datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert result.stac_collection == "sentinel-2-l2a"
    assert result.index == "EVI"


def test_raster_calculation_inputs() -> None:
    data = {
        "aoi": TEST_HEATHROW_AOI,
        "bbox": None,
        "date_start": "2024-01-01T00:00:00Z",
        "date_end": "2024-01-01T00:00:00Z",
        "stac_collection": "sentinel-2-l2a",
        "index": "EVI",
    }

    # Act
    result = RasterCalculatorFunctionInputs(**data).as_ogc_process_inputs()

    # Assert
    assert json.loads(result["aoi"]) == TEST_HEATHROW_AOI
    assert "bbox" not in result
    assert result["date_start"] == "2024-01-01T00:00:00+00:00"
    assert result["date_end"] == "2024-01-01T00:00:00+00:00"
    assert result["stac_collection"] == "sentinel-2-l2a"
    assert result["index"] == "EVI"
