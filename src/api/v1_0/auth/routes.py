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
TIMEOUT = 30


def decode_token(token: str, *, ws: bool = False) -> dict[str, Any]:
    optional_custom_headers = {"User-agent": "custom-user-agent"}
    jwks_client = PyJWKClient(current_settings().eodh_auth.certs_url, headers=optional_custom_headers)

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


def validate_token_from_websocket(token: str) -> tuple[str, dict[str, Any]]:
    if not token or not token.startswith("Bearer "):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication credentials")

    token = token.replace("Bearer ", "")

    return token, decode_token(token, ws=True)


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
    async with aiohttp.ClientSession() as session, session.post(
        url=settings.eodh_auth.token_url,
        headers=_HEADERS,
        data={
            "client_id": settings.eodh_auth.client_id,
            "client_secret": settings.eodh_auth.client_secret,
            "username": token_request.username,
            "password": token_request.password,
            "grant_type": "password",
            "scope": "offline_access",
        },
        timeout=TIMEOUT,
    ) as response:
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
    settings: Annotated[Settings, Depends(current_settings)],
) -> IntrospectResponse:
    async with aiohttp.ClientSession() as session, session.post(
        settings.eodh_auth.introspect_url,
        headers=_HEADERS,
        data={
            "client_id": settings.eodh_auth.client_id,
            "client_secret": settings.eodh_auth.client_secret,
            "token": credential.credentials,
        },
        timeout=TIMEOUT,
    ) as response:
        if response.status != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status, detail=await response.json())
        return IntrospectResponse(**await response.json())
