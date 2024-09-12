from __future__ import annotations

from urllib.parse import urljoin

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src import consts


class OAuth2Settings(BaseModel):
    base_url: str
    realm: str
    username: str | None = None
    password: str | None = None
    client_id: str
    client_secret: str

    @property
    def oid_url(self) -> str:
        return urljoin(self.base_url, f"/keycloak/realms/{self.realm}/protocol/openid-connect")

    @property
    def token_url(self) -> str:
        return self.oid_url + "/token"

    @property
    def auth_url(self) -> str:
        return self.oid_url + "/auth"

    @property
    def introspect_url(self) -> str:
        return self.token_url + "/introspect"

    @property
    def certs_url(self) -> str:
        return self.oid_url + "/certs"


class Settings(BaseSettings):
    """Represents Application Settings with nested configuration sections."""

    environment: str = "local"
    api_key: str
    eodh_auth: OAuth2Settings

    model_config = SettingsConfigDict(
        env_file=consts.directories.ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


def current_settings() -> Settings:
    return Settings()
