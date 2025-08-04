from __future__ import annotations

import json
import pathlib
import typing

import pytest
import requests
from starlette.testclient import TestClient

from app import app as fast_api_app
from src import consts
from src.core.settings import current_settings

if typing.TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.python import Function
    from fastapi import FastAPI


def pytest_collection_modifyitems(config: Config, items: list[Function]) -> None:  # noqa: ARG001
    rootdir = pathlib.Path(consts.directories.ROOT_DIR)
    for item in items:
        rel_path = pathlib.Path(item.fspath).relative_to(rootdir)
        mark_name = rel_path.as_posix().split("/")[1]
        mark = getattr(pytest.mark, mark_name)
        item.add_marker(mark)


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return fast_api_app


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_token_module_scoped() -> str:
    settings = current_settings()
    client = TestClient(fast_api_app)
    response = client.post(
        "/api/v1.2/auth/token",
        json={"username": settings.eodh.username, "password": settings.eodh.password},
    )
    return response.json()["access_token"]  # type: ignore[no-any-return]


@pytest.fixture
def auth_token_func_scoped() -> str:
    settings = current_settings()
    client = TestClient(fast_api_app)
    response = client.post(
        "/api/v1.2/auth/token",
        json={"username": settings.eodh.username, "password": settings.eodh.password},
    )
    return response.json()["access_token"]  # type: ignore[no-any-return]


@pytest.fixture(scope="session")
def auth_token_session_scoped() -> str:
    settings = current_settings()
    client = TestClient(fast_api_app)
    response = client.post(
        "/api/v1.2/auth/token",
        json={"username": settings.eodh.username, "password": settings.eodh.password},
    )
    return response.json()["access_token"]  # type: ignore[no-any-return]


@pytest.fixture(scope="session")
def ws_token(auth_token_session_scoped: str) -> typing.Generator[str]:
    settings = current_settings()

    response = requests.post(
        settings.eodh.workspace_tokens_url,
        headers={"Authorization": f"Bearer {auth_token_session_scoped}"},
        timeout=30,
        json={"name": "API Token", "scope": "offline_access", "expires": 30},
    )

    token_response = json.loads(response.text)
    token = token_response["token"]
    yield token

    requests.delete(
        f"{settings.eodh.workspace_tokens_url}/{token_response['id']}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
