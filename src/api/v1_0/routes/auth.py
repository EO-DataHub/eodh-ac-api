from __future__ import annotations

from typing import Annotated, Any

import jwt
import jwt.exceptions
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient  # type: ignore[attr-defined]
from pydantic import BaseModel

from src.core.settings import current_settings


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


auth_router_v1_0 = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

jwt_bearer_scheme = HTTPBearer()


async def valid_access_token(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],
) -> dict[str, Any]:
    optional_custom_headers = {"User-agent": "custom-user-agent"}
    jwks_client = PyJWKClient(current_settings().eodh_auth.certs_url, headers=optional_custom_headers)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(credential.credentials)
        return jwt.decode(
            credential.credentials,
            signing_key.key,
            audience=["oauth2-proxy-workspaces", "oauth2-proxy", "account"],
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
    except jwt.exceptions.InvalidTokenError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex


async def get_current_user(token_data: Annotated[dict[str, Any], Depends(valid_access_token)]) -> User:
    return User(
        username=token_data["sub"],
        email=token_data.get("email"),
        full_name=token_data.get("name"),
        disabled=token_data.get("disabled", False),
    )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=401, detail="Inactive user")
    return current_user


@auth_router_v1_0.get("/users/me")
async def get_my_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
