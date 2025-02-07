from __future__ import annotations

import asyncio
import math
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError
from starlette import status

from src.api.v1_0.action_creator.schemas import (
    FUNCTION_TO_INPUTS_LOOKUP,
    ActionCreatorFunctionSpec,
    ActionCreatorJob,
    ActionCreatorJobSummary,
    ActionCreatorSubmissionRequest,
    ActionCreatorSubmissionsQueryParams,
    ErrorResponse,
    FunctionsResponse,
    PaginationResults,
)
from src.api.v1_0.auth.routes import decode_token, validate_access_token, validate_token_from_websocket
from src.services.ades.factory import ades_client_factory
from src.services.ades.schemas import StatusCode
from src.services.db.action_creator_repo import ActionCreatorRepository, get_function_repo
from src.utils.logging import get_logger

_logger = get_logger(__name__)
TCreationSpec = Annotated[
    ActionCreatorSubmissionRequest,
    Body(
        openapi_examples={
            "ndvi": {
                "summary": "NDVI",
                "description": "Calculate NDVI",
                "value": {
                    "preset_function": {
                        "function_identifier": "raster-calculate",
                        "inputs": {
                            "aoi": {
                                "coordinates": [
                                    [
                                        [14.763294437090849, 50.833598186651244],
                                        [15.052268923898112, 50.833598186651244],
                                        [15.052268923898112, 50.989077215056824],
                                        [14.763294437090849, 50.989077215056824],
                                        [14.763294437090849, 50.833598186651244],
                                    ]
                                ],
                                "type": "Polygon",
                            },
                            "date_start": "2024-04-03T00:00:00",
                            "date_end": "2024-08-01T00:00:00",
                            "index": "NDVI",
                            "stac_collection": "sentinel-2-l2a",
                            "limit": 25,
                        },
                    }
                },
            },
            "land-cover-change-detection-esa-global-lc": {
                "summary": "Land Cover Change Detection - ESA Global Land Cover",
                "description": "Calculate Land Cover class changes across time-series of STAC items from selected "
                "collection",
                "value": {
                    "preset_function": {
                        "function_identifier": "lulc-change",
                        "inputs": {
                            "aoi": {
                                "coordinates": [
                                    [
                                        [14.763294437090849, 50.833598186651244],
                                        [15.052268923898112, 50.833598186651244],
                                        [15.052268923898112, 50.989077215056824],
                                        [14.763294437090849, 50.989077215056824],
                                        [14.763294437090849, 50.833598186651244],
                                    ]
                                ],
                                "type": "Polygon",
                            },
                            "date_start": "2006-01-01T00:00:00",
                            "date_end": "2024-04-03T00:00:00",
                            "stac_collection": "esacci-globallc",
                        },
                    }
                },
            },
            "land-cover-change-detection-corine": {
                "summary": "Land Cover Change Detection - CORINE",
                "description": "Calculate Land Cover class changes across time-series of STAC items from selected "
                "collection",
                "value": {
                    "preset_function": {
                        "function_identifier": "lulc-change",
                        "inputs": {
                            "aoi": {
                                "coordinates": [
                                    [
                                        [14.763294437090849, 50.833598186651244],
                                        [15.052268923898112, 50.833598186651244],
                                        [15.052268923898112, 50.989077215056824],
                                        [14.763294437090849, 50.989077215056824],
                                        [14.763294437090849, 50.833598186651244],
                                    ]
                                ],
                                "type": "Polygon",
                            },
                            "date_start": "2006-01-01T00:00:00",
                            "date_end": "2024-04-03T00:00:00",
                            "stac_collection": "clms-corinelc",
                        },
                    }
                },
            },
            "land-cover-change-detection-water-bodies": {
                "summary": "Land Cover Change Detection - Water Bodies",
                "description": "Calculate Land Cover class changes across time-series of STAC items from selected "
                "collection",
                "value": {
                    "preset_function": {
                        "function_identifier": "lulc-change",
                        "inputs": {
                            "aoi": {
                                "coordinates": [
                                    [
                                        [14.763294437090849, 50.833598186651244],
                                        [15.052268923898112, 50.833598186651244],
                                        [15.052268923898112, 50.989077215056824],
                                        [14.763294437090849, 50.989077215056824],
                                        [14.763294437090849, 50.833598186651244],
                                    ]
                                ],
                                "type": "Polygon",
                            },
                            "date_start": "2006-01-01T00:00:00",
                            "date_end": "2024-04-03T00:00:00",
                            "stac_collection": "clms-water-bodies",
                        },
                    }
                },
            },
        }
    ),
]

action_creator_router_v1_0 = APIRouter(
    prefix="/action-creator",
    tags=["Action Creator"],
)


@action_creator_router_v1_0.get(
    "/functions",
    response_model=FunctionsResponse,
    response_model_exclude_unset=False,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def get_available_functions(
    repo: Annotated[ActionCreatorRepository, Depends(get_function_repo)],
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],  # noqa: ARG001
    collection: Annotated[str | None, Query(max_length=64, description="STAC collection")] = None,
) -> FunctionsResponse:
    _, results = repo.get_available_functions(collection)
    return FunctionsResponse(functions=[ActionCreatorFunctionSpec(**f) for f in results], total=len(results))


@action_creator_router_v1_0.post(
    "/submissions",
    response_model=ActionCreatorJob,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": ErrorResponse,
        }
    },
)
async def submit_function(
    creation_spec: TCreationSpec,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJob:
    introspected_token = decode_token(credential.credentials)

    ades = ades_client_factory(workspace=introspected_token["preferred_username"], token=credential.credentials)

    inputs_cls = FUNCTION_TO_INPUTS_LOOKUP[creation_spec.preset_function.function_identifier]
    inputs = inputs_cls(**creation_spec.preset_function.inputs).as_ogc_process_inputs()

    err, _ = await ades.reregister_process(creation_spec.preset_function.function_identifier)

    if err is not None:
        raise HTTPException(
            status_code=err.code,
            detail=err.detail,
        )

    err, response = await ades.execute_process(
        process_identifier=creation_spec.preset_function.function_identifier,
        process_inputs=inputs,
    )

    if err is not None:  # Will happen if there are race conditions and the process was deleted or ADES is unresponsive
        raise HTTPException(
            status_code=err.code,
            detail=err.detail,
        )

    if response is None:  # Impossible case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing preset function",
        )

    return ActionCreatorJob(
        submission_id=response.job_id,
        spec=creation_spec,
        status=response.status.value,
        submitted_at=response.created,
    )


@action_creator_router_v1_0.websocket("/ws/submissions")
async def submit_function_websocket(  # noqa: C901
    websocket: WebSocket,
) -> None:
    await websocket.accept()

    try:
        # Manually get the Authorization header and validate it
        token, introspected_token = validate_token_from_websocket(websocket.headers.get("Authorization"))

        # Receive the submission request from the client
        try:
            creation_spec = ActionCreatorSubmissionRequest(**await websocket.receive_json())
        except ValidationError as e:
            # Manually construct a validation error response
            error_response = {
                "detail": [{"loc": ["body", *err["loc"]], "msg": err["msg"], "type": err["type"]} for err in e.errors()]
            }
            await websocket.send_json({"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "result": error_response})
            raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA, reason="Data validation error") from e

        if creation_spec.preset_function.function_identifier not in FUNCTION_TO_INPUTS_LOOKUP:
            raise WebSocketException(
                code=status.WS_1003_UNSUPPORTED_DATA,
                reason=f"Function '{creation_spec.preset_function.function_identifier}' not found. "
                "Please use `/functions` endpoint to get list of supported functions.",
            )

        inputs_cls = FUNCTION_TO_INPUTS_LOOKUP[creation_spec.preset_function.function_identifier]
        inputs = inputs_cls(**creation_spec.preset_function.inputs).as_ogc_process_inputs()

        ades = ades_client_factory(token=token, workspace=introspected_token["preferred_username"])

        err = await ades.ensure_process_exists(creation_spec.preset_function.function_identifier)

        if err is not None:
            await websocket.send_json({
                "status_code": err.code,
                "result": err.detail,
            })
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=err.detail,
            )

        err, execution_result = await ades.execute_process(
            process_identifier=creation_spec.preset_function.function_identifier,
            process_inputs=inputs,
        )

        if (
            err is not None
        ):  # Will happen if there are race conditions and the process was deleted or ADES is unresponsive
            await websocket.send_json({
                "status_code": err.code,
                "result": err.detail,
            })
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=err.detail,
            )

        if execution_result is None:  # Impossible case
            await websocket.send_json({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "result": "An error occurred while executing function",
            })
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="An error occurred while executing function",
            )

        await websocket.send_json({
            "status_code": status.HTTP_202_ACCEPTED,
            "result": ActionCreatorJob(
                submission_id=execution_result.job_id,
                spec=creation_spec,
                status=execution_result.status.value,
                submitted_at=execution_result.created,
            ).model_dump(mode="json"),
        })

        while True:
            err, status_result = await ades.get_job_details(execution_result.job_id)

            if err is not None:
                await websocket.send_json({
                    "status_code": err.code,
                    "result": err.detail,
                })
                raise WebSocketException(
                    code=status.WS_1011_INTERNAL_ERROR,
                    reason=err.detail,
                )

            if status_result is None:
                raise WebSocketException(
                    code=status.WS_1011_INTERNAL_ERROR,
                    reason="An unknown error occurred while polling for the Job execution status",
                )

            if status_result.status != StatusCode.running:
                break

            await asyncio.sleep(5)

        await websocket.send_json({
            "status_code": status.HTTP_200_OK,
            "result": ActionCreatorJobSummary(
                submission_id=status_result.job_id,
                function_identifier=status_result.process_id,
                status=status_result.status.value,
                submitted_at=status_result.created,
                finished_at=status_result.finished,
            ).model_dump(mode="json"),
        })
    except WebSocketDisconnect:
        _logger.info("Websocket disconnected")
        raise
    finally:
        await websocket.close()


@action_creator_router_v1_0.get(
    "/submissions",
    response_model=PaginationResults[ActionCreatorJobSummary],
    response_model_exclude_unset=False,
    response_model_exclude_none=False,
    status_code=status.HTTP_200_OK,
)
async def get_function_submissions(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
    params: Annotated[ActionCreatorSubmissionsQueryParams, Query()],
) -> dict[str, Any]:
    introspected_token = decode_token(credential.credentials)
    username = introspected_token["preferred_username"]
    ades = ades_client_factory(workspace=username, token=credential.credentials)

    # Get the jobs
    ades_jobs: dict[str, Any]
    err, ades_jobs = await ades.list_job_submissions(raw_output=True)  # type: ignore[assignment]

    if err is not None:
        raise HTTPException(status_code=err.code, detail=err.detail)

    if ades_jobs is None:  # Impossible case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing preset function",
        )

    # To result schema
    results = [
        {
            "submission_id": job["jobID"],
            "function_identifier": job["processID"],
            "status": job["status"],
            "submitted_at": job["created"],
            "finished_at": job.get("finished"),
            "successful": job["status"] == "successful",
        }
        for job in ades_jobs["jobs"]
    ]

    # Order by
    # Use tuples to handle None items - tuples are sorted item by item
    results.sort(
        key=lambda x: (x[params.order_by] is None, x[params.order_by]),
        reverse=params.order_direction == "desc",
    )

    # Paginate
    offset = (params.page - 1) * params.per_page
    total_pages = math.ceil(len(ades_jobs["jobs"]) / params.per_page)
    limited_jobs = results[offset : offset + params.per_page]

    return {
        "results": limited_jobs,
        "total_items": len(ades_jobs["jobs"]),  # Use len() as ADES returns count for the unregistered processes too
        "total_pages": total_pages,
        "ordered_by": params.order_by,
        "order_direction": params.order_direction,
        "current_page": params.page,
        "results_on_current_page": len(limited_jobs),
        "results_per_page": params.per_page,
    }


@action_creator_router_v1_0.get(
    "/submissions/{submission_id}",
    response_model=ActionCreatorJobSummary,
    response_model_exclude_unset=False,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": ErrorResponse}},
)
async def get_function_submission_status(
    submission_id: uuid.UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> ActionCreatorJobSummary:
    introspected_token = decode_token(credential.credentials)
    username = introspected_token["preferred_username"]
    ades = ades_client_factory(workspace=username, token=credential.credentials)
    err, job = await ades.get_job_details(job_id=submission_id)

    if err:
        raise HTTPException(status_code=err.code, detail=err.detail)

    if job is None:
        # This should never happen if error was not generated
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return ActionCreatorJobSummary(
        submission_id=job.job_id,
        function_identifier=job.process_id,
        status=job.status if job.status != "dismissed" else "cancelled",
        submitted_at=job.created,
        finished_at=job.finished,
    )


@action_creator_router_v1_0.delete(
    "/submissions/{submission_id}",
    status_code=204,
    response_model=None,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": ErrorResponse}},
)
async def cancel_function_execution(
    submission_id: uuid.UUID,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> None:
    introspected_token = decode_token(credential.credentials)
    username = introspected_token["preferred_username"]
    ades = ades_client_factory(workspace=username, token=credential.credentials)
    err, _ = await ades.cancel_or_delete_job(submission_id)
    if err:
        raise HTTPException(status_code=err.code, detail=err.detail)
