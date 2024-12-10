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


def auth_token() -> str:
    settings = current_settings()
    client = TestClient(fast_api_app)
    response = client.post(
        "/api/v1.0/auth/token",
        json={"username": settings.eodh_auth.username, "password": settings.eodh_auth.password},
    )
    return response.json()["access_token"]  # type: ignore[no-any-return]


@pytest.fixture(scope="session")
def ws_token() -> typing.Generator[str]:
    settings = current_settings()

    response = requests.post(
        settings.eodh_auth.workspace_tokens_url,
        headers={"Authorization": f"Bearer {settings.eodh_auth.api_token}"},
        timeout=30,
    )

    token_response = json.loads(response.text)
    yield token_response["token"]

    requests.delete(
        f"{settings.eodh_auth.workspace_tokens_url}/{token_response['id']}",
        headers={"Authorization": f"Bearer {settings.eodh_auth.api_token}"},
        timeout=30,
    )
