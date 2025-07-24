from __future__ import annotations

from typing import Annotated, Any

import aiohttp
import jwt
import jwt.exceptions
from fastapi import APIRouter, Depends, HTTPException, WebSocketException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient  # type: ignore[attr-defined]

from src.api.v1_0.auth.schemas import IntrospectResponse, TokenRequest, TokenResponse
from src.core.settings import Settings, current_settings

_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

auth_router_v1_0 = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

jwt_bearer_scheme = HTTPBearer()
optional_jwt_bearer_scheme = HTTPBearer(auto_error=False)
TIMEOUT = 30


def decode_token(token: str, *, ws: bool = False) -> dict[str, Any]:
    optional_custom_headers = {"User-agent": "custom-user-agent"}
    jwks_client = PyJWKClient(current_settings().eodh.certs_url, headers=optional_custom_headers)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            audience=["oauth2-proxy-workspaces", "oauth2-proxy", "account"],
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
    except jwt.exceptions.PyJWTError as ex:
        if ws:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid authentication credentials",
            ) from ex
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex


def validate_access_token(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],
) -> HTTPAuthorizationCredentials:
    decode_token(credential.credentials)
    return credential


def validate_access_token_if_provided(
    credential: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_jwt_bearer_scheme)] = None,
) -> HTTPAuthorizationCredentials | None:
    if credential is None:
        return None
    decode_token(credential.credentials)
    return credential


def validate_token_from_websocket(token: str) -> tuple[str, dict[str, Any]]:
    if not token or not token.startswith("Bearer "):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication credentials")

    token = token.replace("Bearer ", "")

    return token, decode_token(token, ws=True)


def try_get_workspace_from_token_or_request_body(
    introspected_token: dict[str, Any],
    workspace_from_request_body: str | None = None,
) -> str:
    if workspace_from_request_body is not None:
        return workspace_from_request_body

    parsed_token = IntrospectResponse(**introspected_token)
    if parsed_token.workspaces:
        # Take first workspace from the WS list
        return parsed_token.workspaces[0]
    if parsed_token.preferred_username is not None:
        # As a fallback take preferred username if present
        return parsed_token.preferred_username
    # Raise exception otherwise
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")


@auth_router_v1_0.post(
    "/token",
    response_model=TokenResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request - Request was malformed",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized - Invalid client or Invalid client credentials",
        },
    },
)
async def authenticate(
    token_request: TokenRequest,
    settings: Annotated[Settings, Depends(current_settings)],
) -> TokenResponse:
    async with (
        aiohttp.ClientSession() as session,
        session.post(
            url=settings.eodh.token_url,
            headers=_HEADERS,
            data={
                "client_id": settings.eodh.client_id,
                "username": token_request.username,
                "password": token_request.password,
                "grant_type": "password",
                "scope": "openid",
            },
            timeout=TIMEOUT,
        ) as response,
    ):
        if response.status != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status, detail=await response.json())
        return TokenResponse(**await response.json())


@auth_router_v1_0.post(
    "/token/introspection",
    response_model=IntrospectResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request - Request was malformed",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized - Invalid token",
        },
    },
)
async def token_introspection(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(validate_access_token)],
) -> IntrospectResponse:
    dec = decode_token(credential.credentials)
    return IntrospectResponse(**dec)
