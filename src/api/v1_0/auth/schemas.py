from __future__ import annotations

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    username: str
    password: str


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
    exp: int | None = None
    iat: int | None = None
    jti: str | None = None
    iss: str | None = None
    aud: list[str] | None = None
    sub: str | None = None
    typ: str | None = None
    arc: str | None = None
    azp: str | None = None
    session_state: str | None = None
    allowed_origins: list[str] | None = Field(None, alias="allowed-origins")
    realm_access: RealmAccess | None = None
    resource_access: ResourceAccess | None = None
    scope: str | None = None
    sid: str | None = None
    email_verified: bool | None = None
    name: str | None = None
    preferred_username: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: str | None = None
    client_id: str | None = None
    username: str | None = None
    token_type: str | None = None
    active: bool | None = None
