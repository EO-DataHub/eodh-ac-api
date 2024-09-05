from __future__ import annotations

from pydantic import BaseModel, Field


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    active: bool | None = None


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    token_type: str
    not_before_policy: int = Field(..., alias="not-before-policy")
    session_state: str
    scope: str


class RealmAccess(BaseModel):
    roles: list[str]


class Account(BaseModel):
    roles: list[str]


class ResourceAccess(BaseModel):
    account: Account


class IntrospectResponse(BaseModel):
    exp: int
    iat: int
    jti: str
    iss: str
    aud: list[str]
    sub: str
    typ: str
    azp: str
    session_state: str
    allowed_origins: list[str] = Field(..., alias="allowed-origins")
    realm_access: RealmAccess
    resource_access: ResourceAccess
    scope: str
    sid: str
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str
    client_id: str
    username: str
    token_type: str
    active: bool
