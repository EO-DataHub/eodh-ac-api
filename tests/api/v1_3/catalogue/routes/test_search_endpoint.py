from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from starlette import status

from src.services.stac.client import SUPPORTED_DATASETS
from tests.api.v1_3.catalogue.conftest import DATA_DIR

if TYPE_CHECKING:
    from httpx import Response
    from starlette.testclient import TestClient

SEARCH_ENDPOINT_PATH = "/api/v1.3/catalogue/stac/search"
STAC_SEARCH_PAYLOAD = json.loads((DATA_DIR / "stac-search" / "search.json").read_text())


def _send_search_request(
    client: TestClient,
    token: str,
    stac_query: dict[str, Any] | None = None,
) -> Response:
    return client.post(
        url=SEARCH_ENDPOINT_PATH,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json=stac_query,
    )


def test_should_return_401_when_invalid_user_credentials(client: TestClient) -> None:
    # Act
    response = _send_search_request(client, token="dummy-token")  # noqa: S106

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_should_return_404_when_collection_is_not_found(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Act
    response = _send_search_request(client, token=auth_token_module_scoped, stac_query={"dummy-collection": {}})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"Collections: ['dummy-collection'] are not supported. "
        f"Supported collections: {', '.join(SUPPORTED_DATASETS)}"
    }


def test_should_merge_results_from_multiple_datasets(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    expected_collections = {"sentinel2_ard"}

    # Act
    response = client.post(
        SEARCH_ENDPOINT_PATH,
        json=STAC_SEARCH_PAYLOAD,
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK, "Expected HTTP 200 OK"
    json_resp = response.json()
    assert json_resp["items"]["type"] == "FeatureCollection", "Response must be a FeatureCollection"
    assert "features" in json_resp["items"], "FeatureCollection must contain 'features'"

    features: list[dict[str, Any]] = json_resp["items"]["features"]
    assert len(features) > 0, "Expected at least one feature in response"

    # Validate sorting - datetime should be descending
    # We'll skip any feature that doesn't have 'properties.datetime'
    # to avoid raising KeyError. The endpoint already handles that gracefully.
    datetimes = [f["properties"]["datetime"] for f in features if "datetime" in f["properties"]]
    # Check if the list is sorted descending
    # A quick approach is to compare it with its sorted copy.
    sorted_desc = sorted(datetimes, reverse=True)
    assert datetimes == sorted_desc, "Features must be sorted by datetime descending"

    returned_collections = {feat["collection"] for feat in features}
    assert returned_collections == expected_collections
    assert all(token is not None for coll, token in json_resp["continuation_tokens"].items())


def test_should_paginate_until_no_more_results(
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    max_pages = 10  # Define max_pages so that we can break the loop just in case
    payload = {"sentinel-2-l2a-ard": STAC_SEARCH_PAYLOAD["sentinel-2-l2a-ard"]}
    payload["sentinel-2-l2a-ard"]["limit"] = 20

    response = client.post(
        SEARCH_ENDPOINT_PATH,
        json=payload,
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK, "Expected HTTP 200 OK"

    page_count = 1
    while True:
        payload["sentinel-2-l2a-ard"]["token"] = response.json()["continuation_tokens"]["sentinel-2-l2a-ard"]
        response = client.post(
            SEARCH_ENDPOINT_PATH,
            json=payload,
            headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        )
        assert response.status_code == status.HTTP_200_OK, "Expected HTTP 200 OK"
        assert response.json()["items"]["features"]

        if response.json()["continuation_tokens"]["sentinel-2-l2a-ard"] is None:
            break

        page_count += 1

        if page_count > max_pages:
            break
