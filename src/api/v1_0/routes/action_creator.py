from __future__ import annotations

import typing
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_hypermodel import (
    HALResponse,
)
from geojson_pydantic import Polygon
from pydantic import UUID4  # noqa: TCH002
from starlette import status

from src.api.v1_0.routes.auth import jwt_bearer_scheme  # noqa: TCH001
from src.api.v1_0.schemas import (
    ActionCreatorFunctionSpec,
    ActionCreatorJob,
    ActionCreatorJobStatus,
    ActionCreatorSubmissionRequest,
    FunctionCollection,
)
from src.consts.action_creator import FUNCTIONS
from src.services.action_creator_repo import ActionCreatorRepository

if typing.TYPE_CHECKING:
    from fastapi.security import HTTPAuthorizationCredentials

action_creator_router_v1_0 = APIRouter(
    prefix="/action-creator",
    tags=["Action Creator"],
)


def get_function_repo() -> ActionCreatorRepository:
    return ActionCreatorRepository(FUNCTIONS)


@action_creator_router_v1_0.get(
    "/functions",
    response_model=FunctionCollection,
    response_model_exclude_unset=True,
    response_class=HALResponse,
)
async def get_available_functions(
    repo: Annotated[ActionCreatorRepository, Depends(get_function_repo)],
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],  # noqa: ARG001
) -> FunctionCollection:
    return FunctionCollection(functions=[ActionCreatorFunctionSpec(**f) for f in repo.get_available_functions()])


@action_creator_router_v1_0.get(
    "/functions/{collection}",
    response_model=FunctionCollection,
    response_model_exclude_unset=True,
    response_class=HALResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Collection Not found",
        }
    },
)
async def get_available_functions_for_collection(
    collection: str,
    repo: Annotated[ActionCreatorRepository, Depends(get_function_repo)],
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],  # noqa: ARG001
) -> FunctionCollection:
    return FunctionCollection(
        functions=[ActionCreatorFunctionSpec(**f) for f in repo.get_available_functions_for_collection(collection)]
    )


@action_creator_router_v1_0.post(
    "/submissions",
    response_model=ActionCreatorJob,
    response_model_exclude_unset=True,
    response_class=HALResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_function(
    creation_spec: ActionCreatorSubmissionRequest,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],  # noqa: ARG001
) -> ActionCreatorJob:
    return ActionCreatorJob(
        correlation_id=uuid.uuid4(),
        spec=creation_spec,
        status=ActionCreatorJobStatus.submitted,
        submitted_at=datetime.now(tz=timezone.utc),
    )


@action_creator_router_v1_0.get(
    "/submissions",
    response_model=list[ActionCreatorJob],
    response_model_exclude_unset=True,
    response_class=HALResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_function_submissions(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],  # noqa: ARG001
) -> list[ActionCreatorJob]:
    return [
        ActionCreatorJob(
            correlation_id=uuid.uuid4(),
            spec=ActionCreatorSubmissionRequest(
                function_name="raster_calculator",
                function_params={
                    "collection": "sentinel-2-l2a",
                    "date_range_start": datetime.now(tz=timezone.utc),
                    "date_range_end": datetime.now(tz=timezone.utc),
                    "aoi": Polygon(
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
                },
            ),
            status=ActionCreatorJobStatus.submitted,
            submitted_at=datetime.now(tz=timezone.utc),
        )
        for _ in range(3)
    ]


@action_creator_router_v1_0.get(
    "/submissions/{correlation_id}",
    response_model=ActionCreatorJob,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_status(
    correlation_id: UUID4,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],  # noqa: ARG001
) -> ActionCreatorJob:
    return ActionCreatorJob(
        correlation_id=correlation_id,
        spec=ActionCreatorSubmissionRequest(
            function_name="raster_calculator",
            function_params={
                "collection": "sentinel-2-l2a",
                "date_range_start": datetime.now(tz=timezone.utc),
                "date_range_end": datetime.now(tz=timezone.utc),
                "aoi": Polygon(
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
            },
        ),
        status=ActionCreatorJobStatus.submitted,
        submitted_at=datetime.now(tz=timezone.utc),
    )


@action_creator_router_v1_0.delete(
    "/submissions/{correlation_id}",
    status_code=204,
    response_model=None,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def cancel(
    correlation_id: UUID4,  # noqa: ARG001
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],  # noqa: ARG001
) -> None: ...
