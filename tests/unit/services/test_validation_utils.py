from __future__ import annotations

from typing import Any

import pytest

from src.consts.geometries import HEATHROW_AOI, UK_AOI
from src.services.validation_utils import MAX_AREA_SQ_KM, SQ_MILES_DIVISOR, ensure_area_smaller_than

FEATURES = [
    {
        "type": "Feature",
        "properties": {"id": "heathrow_airport", "area": 40.82},
        "geometry": HEATHROW_AOI,
    },
    {
        "type": "Feature",
        "properties": {"id": "uk", "area": 698816.12},
        "geometry": UK_AOI,
    },
    {
        "type": "Feature",
        "properties": {"id": "almost_error", "area": 999.78612233204638},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-0.359773144792898, 51.409509931388136],
                    [0.142391529267438, 51.409508951725627],
                    [0.143435783429914, 51.153297544977889],
                    [-0.359874759152825, 51.153329186057817],
                    [-0.359773144792898, 51.409509931388136],
                ]
            ],
        },
    },
    {
        "type": "Feature",
        "properties": {"id": "almost_not_error", "area": 1001.5906603666056},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-0.359772039935723, 51.40950919261644],
                    [0.142392915191919, 51.409510598842985],
                    [0.143435492108673, 51.153297327560075],
                    [-0.360845952300241, 51.15290129618338],
                    [-0.359772039935723, 51.40950919261644],
                ]
            ],
        },
    },
    {
        "type": "Feature",
        "properties": {"id": "square_indian_ocean", "area": 11673189.830378208},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [48.93930743807514, -5.732785505670838],
                    [80.448639900435737, -5.732785505670838],
                    [80.448639900435737, 24.43040238139325],
                    [48.93930743807514, 24.43040238139325],
                    [48.93930743807514, -5.732785505670838],
                ]
            ],
        },
    },
    {
        "type": "Feature",
        "properties": {"id": "circle_indian_ocean", "area": 13431244.518241877},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [81.534618016578108, 12.097248184031381],
                    [81.162950207449882, 15.759203109786172],
                    [80.062229765536273, 19.219422967539497],
                    [78.274756760128895, 22.345462740168887],
                    [75.869222776399155, 25.029327878200554],
                    [72.938071136302753, 27.189203208005459],
                    [69.593944353559863, 28.767685691544294],
                    [65.965355345023369, 29.728061547621195],
                    [62.191748751355142, 30.05029344771302],
                    [58.418142157686923, 29.728061547621195],
                    [54.789553149150414, 28.767685691544294],
                    [51.445426366407524, 27.18920320800547],
                    [48.514274726311129, 25.029327878200554],
                    [46.108740742581382, 22.345462740168887],
                    [44.321267737174011, 19.219422967539497],
                    [43.22054729526041, 15.759203109786183],
                    [42.848879486132176, 12.097248184031383],
                    [43.22054729526041, 8.384450734830761],
                    [44.321267737174011, 4.780391611836187],
                    [46.108740742581375, 1.441668531209612],
                    [48.514274726311129, -1.489163271406582],
                    [51.445426366407517, -3.891868684815111],
                    [54.7895531491504, -5.673045750493267],
                    [58.418142157686916, -6.767269124286885],
                    [62.191748751355142, -7.136203945176852],
                    [65.965355345023369, -6.767269124286885],
                    [69.593944353559877, -5.673045750493269],
                    [72.938071136302753, -3.891868684815115],
                    [75.869222776399155, -1.489163271406587],
                    [78.274756760128895, 1.441668531209608],
                    [80.062229765536273, 4.780391611836173],
                    [81.162950207449882, 8.384450734830756],
                    [81.534618016578108, 12.097248184031381],
                ]
            ],
        },
    },
    {
        "type": "Feature",
        "properties": {"id": "square_london", "area": 13699.238565104126},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-1.135801099464759, 51.034418208037877],
                    [0.561452155546048, 51.034418208037877],
                    [0.561452155546048, 52.080538774693125],
                    [-1.135801099464759, 52.080538774693125],
                    [-1.135801099464759, 51.034418208037877],
                ]
            ],
        },
    },
    {
        "type": "Feature",
        "properties": {"id": "circle_london", "area": 11048.465874810103},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [0.750497850051941, 51.510198795453533],
                    [0.734010626355435, 51.614263833269995],
                    [0.685182550026431, 51.714105205252352],
                    [0.605890056655154, 51.805924799329816],
                    [0.499180312294117, 51.886251844480775],
                    [0.369154112575602, 51.95206748517257],
                    [0.220808291435259, 52.000910447918194],
                    [0.059843695586216, 52.030961309033081],
                    [-0.107553895823034, 52.041103684882586],
                    [-0.274951487232285, 52.030961309033081],
                    [-0.435916083081328, 52.000910447918194],
                    [-0.584261904221671, 51.95206748517257],
                    [-0.714288103940186, 51.886251844480775],
                    [-0.820997848301223, 51.805924799329816],
                    [-0.900290341672501, 51.714105205252352],
                    [-0.949118418001504, 51.614263833269995],
                    [-0.96560564169801, 51.510198795453533],
                    [-0.949118418001504, 51.405895507268205],
                    [-0.900290341672501, 51.30537565809707],
                    [-0.820997848301223, 51.212540657948885],
                    [-0.714288103940186, 51.131015870151323],
                    [-0.584261904221671, 51.064002498156505],
                    [-0.435916083081328, 51.014144156726005],
                    [-0.274951487232285, 50.983414845808227],
                    [-0.107553895823035, 50.973034230933443],
                    [0.059843695586216, 50.983414845808227],
                    [0.220808291435259, 51.014144156726005],
                    [0.369154112575602, 51.064002498156505],
                    [0.499180312294117, 51.131015870151323],
                    [0.605890056655154, 51.212540657948885],
                    [0.685182550026431, 51.30537565809707],
                    [0.734010626355435, 51.405895507268205],
                    [0.750497850051941, 51.510198795453533],
                ]
            ],
        },
    },
]


@pytest.mark.parametrize(
    "feature",
    FEATURES,
    ids=lambda feature: feature["properties"]["id"],
)
def test_ensure_area_rises_error_if_necessary(feature: dict[str, Any]) -> None:
    if feature["properties"]["area"] > MAX_AREA_SQ_KM:
        with pytest.raises(ValueError, match=f"Area exceeds {MAX_AREA_SQ_KM / SQ_MILES_DIVISOR:,.2f} square miles."):
            ensure_area_smaller_than(geom=feature["geometry"], area_size_limit=MAX_AREA_SQ_KM)
    else:
        ensure_area_smaller_than(geom=feature["geometry"], area_size_limit=MAX_AREA_SQ_KM)
