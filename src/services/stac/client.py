from __future__ import annotations

import abc
import asyncio
import json
from datetime import datetime, timezone
from itertools import starmap
from typing import TYPE_CHECKING, Any, ClassVar, Iterable, Iterator, TypedDict

import aiohttp
from fastapi import HTTPException
from oauthlib.oauth2 import BackendApplicationClient
from pystac_client import Client
from pystac_client.exceptions import APIError
from requests_oauthlib import OAuth2Session
from stac_pydantic.api.extensions.sort import SortDirections, SortExtension
from starlette import status

from src.api.v1_3.catalogue.schemas.stac_search import FetchItemResult
from src.core.settings import current_settings
from src.services.stac.schemas import ExtendedStacSearch, FieldsExtension, StacSearch

if TYPE_CHECKING:
    from geojson_pydantic import Polygon
    from pystac import Item
    from requests import Response


class DatasetLookupRecord(TypedDict):
    catalog_url: str
    collection_name: str
    processor: str


settings = current_settings()

DATASET_LOOKUP: dict[str, DatasetLookupRecord] = {
    "sentinel-1-grd": DatasetLookupRecord(
        catalog_url=f"{settings.eodh_stac_api.endpoint}/catalogs/supported-datasets/earth-search-aws",
        collection_name="sentinel-1-grd",
        processor="Element84",
    ),
    "sentinel-2-l1c": DatasetLookupRecord(
        catalog_url=f"{settings.eodh_stac_api.endpoint}/catalogs/supported-datasets/earth-search-aws",
        collection_name="sentinel-2-l1c",
        processor="Element84",
    ),
    "sentinel-2-l2a": DatasetLookupRecord(
        catalog_url=f"{settings.eodh_stac_api.endpoint}/catalogs/supported-datasets/earth-search-aws",
        collection_name="sentinel-2-l2a",
        processor="Element84",
    ),
    "sentinel-2-l2a-ard": DatasetLookupRecord(
        catalog_url=f"{settings.eodh_stac_api.endpoint}/catalogs/supported-datasets/ceda-stac-catalogue",
        collection_name="sentinel2_ard",
        processor="CEDA",
    ),
    "esa-lccci-glcm": DatasetLookupRecord(
        catalog_url=f"{settings.eodh_stac_api.endpoint}/catalogs/supported-datasets/ceda-stac-catalogue",
        collection_name="land_cover",
        processor="CEDA",
    ),
    "esacci-globallc": DatasetLookupRecord(
        catalog_url=f"{settings.eodh_stac_api.endpoint}/catalogs/supported-datasets/ceda-stac-catalogue",
        collection_name="land_cover",
        processor="CEDA",
    ),
    "clms-corinelc": DatasetLookupRecord(
        catalog_url=settings.sentinel_hub_stac_api.endpoint,
        collection_name="byoc-cbdba844-f86d-41dc-95ad-b3f7f12535e9",
        processor="Synergise",
    ),
    "clms-corine-lc": DatasetLookupRecord(
        catalog_url=settings.sentinel_hub_stac_api.endpoint,
        collection_name="byoc-cbdba844-f86d-41dc-95ad-b3f7f12535e9",
        processor="Synergise",
    ),
    "clms-water-bodies": DatasetLookupRecord(
        catalog_url=settings.sentinel_hub_stac_api.endpoint,
        collection_name="byoc-62bf6f6a-c584-48a8-a739-0bc60efee54a",
        processor="Synergise",
    ),
}
SUPPORTED_DATASETS: set[str] = set(DATASET_LOOKUP.keys())


class StacSearchClientBase(abc.ABC):
    @abc.abstractmethod
    async def fetch_items(
        self,
        collection: str,
        search_params: StacSearch,
    ) -> FetchItemResult: ...

    @abc.abstractmethod
    async def fetch_processing_results(
        self,
        token: str,
        job_id: str,
        stac_api_endpoint: str,
        workspace: str,
        stac_query: StacSearch | None = None,
    ) -> Iterable[Item]: ...

    @abc.abstractmethod
    async def multi_collection_fetch_items(
        self,
        stac_search_query: dict[str, StacSearch],
    ) -> dict[str, Any]: ...

    @abc.abstractmethod
    async def has_items(
        self,
        collection: str,
        area: Polygon,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> bool: ...


class StacSearchClient:
    DATASET_LOOKUP: ClassVar[dict[str, DatasetLookupRecord]] = DATASET_LOOKUP
    SUPPORTED_DATASETS: ClassVar[set[str]] = SUPPORTED_DATASETS

    @staticmethod
    def _sentinel_hub_compliance_hook(response: Response) -> Response:
        response.raise_for_status()
        return response

    @staticmethod
    def _sentinel_hub_auth_token() -> str:
        settings = current_settings()

        client = BackendApplicationClient(client_id=settings.sentinel_hub.client_id)
        oauth = OAuth2Session(client=client)

        oauth.register_compliance_hook("access_token_response", StacSearchClient._sentinel_hub_compliance_hook)

        token = oauth.fetch_token(
            token_url=settings.sentinel_hub.token_url,
            client_secret=settings.sentinel_hub.client_secret,
            include_client_id=True,
        )

        return token["access_token"]  # type: ignore[no-any-return]

    async def fetch_items(
        self,
        collection: str,
        search_params: StacSearch,
    ) -> FetchItemResult:
        lookup = self.DATASET_LOOKUP[collection]

        if search_params.fields is None:
            search_params.fields = FieldsExtension(include=set(), exclude=set())

        if search_params.fields.include is None:
            search_params.fields.include = set()

        search_params.fields.include = search_params.fields.include.union(
            {
                "properties.eo:cloud_cover",
                "properties.grid:code",
                "properties.sar:instrument_mode",
                "properties.sar:polarizations",
                "properties.sat:orbit_state",
            },
        )

        if search_params.sortby is None:
            search_params.sortby = [SortExtension(field="properties.datetime", direction=SortDirections.asc)]

        search_url = f"{lookup['catalog_url']}/search"

        search_model = search_params.model_dump(mode="json", exclude_unset=True, exclude_none=True)
        search_model["collections"] = [lookup["collection_name"]]

        if lookup["processor"] == "Synergise":
            # Pop unsupported fields
            search_model.pop("sortby", None)
            search_model.pop("filter_lang", None)
            search_model.pop("filter", None)
            search_model.pop("fields", None)

            # Filter on datetime in filter field is not supported, and we can't just extract it from the filter
            # field easily. If not set as datetime filter - get all data until now
            search_model["datetime"] = (
                search_model.pop("datetime", None) or f"/{datetime.now(timezone.utc).isoformat()}"
            )

        async with aiohttp.ClientSession() as session, session.post(
            search_url,
            headers={"Authorization": f"Bearer {self._sentinel_hub_auth_token()}", "Accept": "application/geo+json"}
            if lookup["processor"] == "Synergise"
            else None,
            json=search_model,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error when calling EODH STAC API. "
                    f"Status Code: {response.status}: Message: {await response.text()}",
                )
            result = await response.json()

        next_page_link = [link for link in result["links"] if link["rel"] == "next"]
        continuation_token: str | None = None

        if next_page_link:
            continuation_token = next_page_link[0]["body"].get("token", None)

        return FetchItemResult(collection=collection, items=result["features"], token=continuation_token)

    async def fetch_processing_results(  # noqa: PLR6301, RUF100
        self,
        token: str,
        job_id: str,
        stac_api_endpoint: str,
        workspace: str,
        stac_query: StacSearch | None = None,
    ) -> Iterator[Item]:
        try:
            stac_client = Client.open(
                f"{stac_api_endpoint}/catalogs/user-datasets/{workspace}/processing-results/cat_{job_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
        except APIError as ex:
            # User not authorized to access this resource or catalog does not exist
            raise HTTPException(
                status_code=ex.status_code,
                detail=json.loads(str(ex)),
            ) from APIError

        # Sanitize params
        search_params = stac_query or ExtendedStacSearch()

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

        search = stac_client.search(
            limit=search_params.limit,
            ids=search_params.ids,
            collections=search_params.collections,
            intersects=search_params.intersects,
            datetime=search_params.datetime,
            query=search_params.query,
            filter=search_params.filter,
            filter_lang=search_params.filter_lang,
            sortby=[s.model_dump(mode="json") for s in search_params.sortby],
            fields=search_params.fields.model_dump(mode="json"),
        )

        return search.items()  # type: ignore[no-any-return]

    async def multi_collection_fetch_items(
        self,
        stac_search_query: dict[str, StacSearch],
    ) -> dict[str, Any]:
        if diff := set(stac_search_query.keys()).difference(self.SUPPORTED_DATASETS):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collections: {list(diff)} are not supported. "
                f"Supported collections: {', '.join(self.SUPPORTED_DATASETS)}",
            )

        tasks = list(starmap(self.fetch_items, stac_search_query.items()))
        results = await asyncio.gather(*tasks)

        all_items: list[dict[str, Any]] = []
        for _, items, _ in results:
            all_items.extend([i for i in items if i])

        # Sort items by datetime property if present
        # We'll skip items without a valid datetime to avoid errors
        all_items.sort(key=lambda x: x["properties"].get("datetime", ""), reverse=True)

        return {
            "items": {
                "type": "FeatureCollection",
                "features": all_items,
            },
            "continuation_tokens": {collection: token for collection, _, token in results},
            "context": {
                "returned": len(all_items),
                "limit": next(iter(stac_search_query.values())).limit,
            },
        }

    async def has_items(
        self,
        collection: str,
        area: Polygon,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> bool:
        filter_spec = {"op": "s_intersects", "args": [{"property": "geometry"}, area.model_dump(mode="json")]}

        if date_start:
            filter_spec["args"].append({"op": ">=", "args": [{"property": "datetime"}, date_start]})  # type: ignore[attr-defined]
        if date_end:
            filter_spec["args"].append({"op": "<=", "args": [{"property": "datetime"}, date_end]})  # type: ignore[attr-defined]

        items = list(
            await self.fetch_items(
                collection=collection,
                search_params=StacSearch(
                    limit=1,
                    max_items=1,
                    intersects=area.model_dump(mode="json"),
                    fields=FieldsExtension(include=set()),
                    filter=filter_spec,
                ),
            )
        )
        return len(items) > 0


class FakeStacClient(StacSearchClientBase):
    def __init__(
        self,
        *,
        items_to_fetch: FetchItemResult | None = None,
        processing_results_to_fetch: list[Item] | None = None,
        multi_collection_fetch_results: dict[str, Any] | None = None,
        has_results: bool = False,
    ) -> None:
        self.multi_collection_fetch_results = multi_collection_fetch_results
        self.processing_results_to_fetch = processing_results_to_fetch
        self.items_to_fetch = items_to_fetch
        self.has_results = has_results

    async def fetch_items(
        self,
        collection: str,
        search_params: StacSearch,  # noqa: ARG002
    ) -> FetchItemResult:
        return self.items_to_fetch or FetchItemResult(collection, items=[], token=None)

    async def fetch_processing_results(
        self,
        token: str,  # noqa: ARG002
        job_id: str,  # noqa: ARG002
        stac_api_endpoint: str,  # noqa: ARG002
        workspace: str,  # noqa: ARG002
        stac_query: StacSearch | None = None,  # noqa: ARG002
    ) -> Iterable[Item]:
        return self.processing_results_to_fetch or []

    async def multi_collection_fetch_items(
        self,
        stac_search_query: dict[str, StacSearch],
    ) -> dict[str, Any]:
        return self.multi_collection_fetch_results or {k: {} for k in stac_search_query}

    async def has_items(
        self,
        collection: str,  # noqa: ARG002
        area: Polygon,  # noqa: ARG002
        date_start: datetime | None = None,  # noqa: ARG002
        date_end: datetime | None = None,  # noqa: ARG002
    ) -> bool:
        return self.has_results


def stac_client_factory() -> StacSearchClient:
    return StacSearchClient()
