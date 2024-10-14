from __future__ import annotations

import pathlib
import typing

import pytest
from starlette.testclient import TestClient

from app import app as fast_api_app
from src import consts
from src.core.settings import current_settings

if typing.TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.python import Function
    from fastapi import FastAPI

MARKERS = ["unit", "integration", "e2e"]


def pytest_collection_modifyitems(config: Config, items: list[Function]) -> None:  # noqa: ARG001
    rootdir = pathlib.Path(consts.directories.ROOT_DIR)
    for item in items:
        rel_path = pathlib.Path(item.fspath).relative_to(rootdir)
        mark_name = rel_path.as_posix().split("/")[1]
        if mark_name in MARKERS:
            mark = getattr(pytest.mark, mark_name)
            item.add_marker(mark)


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return fast_api_app


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_token() -> str:
    client = TestClient(fast_api_app)
    settings = current_settings()

    response = client.post(
        "/api/v1.0/auth/token",
        json={"username": settings.eodh_auth.username, "password": settings.eodh_auth.password},
    )

    return response.json()["access_token"]  # type: ignore[no-any-return]
