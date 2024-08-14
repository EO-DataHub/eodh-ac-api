from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Security
from fastapi_hypermodel import (
    HALResponse,
)
from geojson_pydantic import Polygon
from pydantic import UUID4  # noqa: TCH002
from starlette import status

from src.routes.security import get_api_key
from src.schemas.action_creator import (
    ActionCreatorFunction,
    ActionCreatorJob,
    ActionCreatorJobStatus,
    ActionCreatorSubmissionRequest,
    CollectionFunctions,
    FunctionCollection,
)

router = APIRouter(
    prefix="/api/v1.0/action-creator",
)


@router.get(
    "/functions",
    response_model=FunctionCollection,
    response_model_exclude_unset=True,
    response_class=HALResponse,
    dependencies=[Security(get_api_key)],
    tags=["Action Creator"],
)
async def get_available_functions() -> FunctionCollection:
    return FunctionCollection(
        functions=[
            CollectionFunctions(
                collection="sentinel-2-l2a",
                functions=[
                    ActionCreatorFunction.evi,
                    ActionCreatorFunction.ndvi,
                    ActionCreatorFunction.ndwi,
                    ActionCreatorFunction.savi,
                ],
            )
        ]
    )


@router.get(
    "/functions/{collection}",
    response_model=FunctionCollection,
    response_model_exclude_unset=True,
    response_class=HALResponse,
    dependencies=[Security(get_api_key)],
    tags=["Action Creator"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Collection Not found",
        }
    },
)
async def get_available_functions_for_collection(collection: str) -> FunctionCollection:
    return FunctionCollection(
        functions=[
            CollectionFunctions(
                collection=collection,
                functions=[
                    ActionCreatorFunction.evi,
                    ActionCreatorFunction.ndvi,
                    ActionCreatorFunction.ndwi,
                    ActionCreatorFunction.savi,
                ],
            )
        ]
    )


@router.post(
    "/submissions",
    response_model=ActionCreatorJob,
    response_model_exclude_unset=True,
    response_class=HALResponse,
    dependencies=[Security(get_api_key)],
    tags=["Action Creator"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_function(creation_spec: ActionCreatorSubmissionRequest) -> ActionCreatorJob:
    return ActionCreatorJob(
        correlation_id=uuid.uuid4(),
        spec=creation_spec,
        status=ActionCreatorJobStatus.submitted,
        submitted_at=datetime.now(tz=timezone.utc),
    )


@router.get(
    "/submissions",
    response_model=list[ActionCreatorJob],
    response_model_exclude_unset=True,
    response_class=HALResponse,
    dependencies=[Security(get_api_key)],
    tags=["Action Creator"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_function_submissions() -> list[ActionCreatorJob]:
    return [
        ActionCreatorJob(
            correlation_id=uuid.uuid4(),
            spec=ActionCreatorSubmissionRequest(
                collection="sentinel-2-l2a",
                function=ActionCreatorFunction.evi,
                date_range_start=datetime.now(tz=timezone.utc),
                date_range_end=datetime.now(tz=timezone.utc),
                aoi=Polygon(
                    type="Polygon",
                    coordinates=[
                        [
                            [0, 0],
                            [0, 0],
                            [0, 0],
                            [0, 0],
                        ]
                    ],
                ),
            ),
            status=ActionCreatorJobStatus.submitted,
            submitted_at=datetime.now(tz=timezone.utc),
        )
        for _ in range(3)
    ]


@router.get(
    "/submissions/{correlation_id}",
    response_model=ActionCreatorJob,
    dependencies=[Security(get_api_key)],
    tags=["Action Creator"],
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_status(correlation_id: UUID4) -> ActionCreatorJob:
    return ActionCreatorJob(
        correlation_id=correlation_id,
        spec=ActionCreatorSubmissionRequest(
            collection="sentinel-2-l2a",
            function=ActionCreatorFunction.evi,
            date_range_start=datetime.now(tz=timezone.utc),
            date_range_end=datetime.now(tz=timezone.utc),
            aoi=Polygon(
                type="Polygon",
                coordinates=[
                    [
                        [0, 0],
                        [0, 0],
                        [0, 0],
                        [0, 0],
                    ]
                ],
            ),
        ),
        status=ActionCreatorJobStatus.submitted,
        submitted_at=datetime.now(tz=timezone.utc),
    )


@router.delete(
    "/submissions/{correlation_id}",
    dependencies=[Security(get_api_key)],
    tags=["Action Creator"],
    status_code=204,
    response_model=None,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def cancel(correlation_id: UUID4) -> None: ...  # noqa: ARG001
