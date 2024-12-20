from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocketException
from pydantic import ValidationError
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.api.v1_0.auth.routes import validate_token_from_websocket
from src.api.v1_1.action_creator.schemas import (
    ActionCreatorJob,
    ActionCreatorJobStatusRequest,
    ActionCreatorJobSummary,
    ActionCreatorSubmissionRequest,
)
from src.consts.functions import FUNCTION_IDENTIFIER_TO_WORKFLOW_MAPPING
from src.services.ades.factory import ades_client_factory
from src.services.ades.schemas import StatusCode
from src.utils.logging import get_logger

_logger = get_logger(__name__)


action_creator_ws_router_v1_1 = APIRouter(
    prefix="/action-creator/ws",
    tags=["Action Creator"],
)


@action_creator_ws_router_v1_1.websocket("/submissions")
async def submit_function_websocket(  # noqa: C901
    websocket: WebSocket,
) -> None:
    await websocket.accept()

    try:
        # Manually get the Authorization header and validate it
        token, introspected_token = validate_token_from_websocket(websocket.headers.get("Authorization"))

        # Receive the submission request from the client
        try:
            workflow_spec = ActionCreatorSubmissionRequest(**await websocket.receive_json())
        except ValidationError as e:
            # Manually construct a validation error response
            error_response = {
                "detail": [{"loc": ["body", *err["loc"]], "msg": err["msg"], "type": err["type"]} for err in e.errors()]
            }
            await websocket.send_json({"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "result": error_response})
            raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA, reason="Data validation error") from e

        workflow_step_spec = next(iter(workflow_spec.workflow.values()))
        wf_identifier = FUNCTION_IDENTIFIER_TO_WORKFLOW_MAPPING[workflow_step_spec.identifier]
        ogc_inputs = workflow_step_spec.inputs.as_ogc_process_inputs()

        if any(step.identifier == "clip" for step in workflow_spec.workflow.values()):
            ogc_inputs["clip"] = "True"

        ades = ades_client_factory(token=token, workspace=introspected_token["preferred_username"])

        err, _ = await ades.reregister_process_v1_1(wf_identifier)

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
            process_identifier=wf_identifier,
            process_inputs=ogc_inputs,
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
                spec=workflow_spec,
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


@action_creator_ws_router_v1_1.websocket("/submission-status")
async def get_job_status_websocket(
    websocket: WebSocket,
) -> None:
    await websocket.accept()

    try:
        # Manually get the Authorization header and validate it
        token, introspected_token = validate_token_from_websocket(websocket.headers.get("Authorization"))

        # Receive the submission status request from the client
        try:
            job_status_request = ActionCreatorJobStatusRequest(**await websocket.receive_json())
        except ValidationError as e:
            # Manually construct a validation error response
            error_response = {
                "detail": [{"loc": ["body", *err["loc"]], "msg": err["msg"], "type": err["type"]} for err in e.errors()]
            }
            await websocket.send_json({"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "result": error_response})
            raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA, reason="Data validation error") from e

        ades = ades_client_factory(token=token, workspace=introspected_token["preferred_username"])

        while True:
            err, status_result = await ades.get_job_details(job_status_request.submission_id)

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
