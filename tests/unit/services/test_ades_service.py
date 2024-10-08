from __future__ import annotations

import os
import re
import shutil
import uuid
from typing import TYPE_CHECKING, Generator
from unittest.mock import MagicMock, patch

import pytest
import yaml

from src import consts
from src.services.ades.client import replace_placeholders_in_cwl_file
from src.services.ades.factory import ades_client_factory

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.monkeypatch import MonkeyPatch

TEST_CWL_FP = consts.directories.TESTS_DIR / "data" / "test-app-package.cwl"


@pytest.fixture
def tmp_cwl_file(tmp_path: Path) -> Generator[Path]:
    shutil.copy(TEST_CWL_FP, tmp_path / TEST_CWL_FP.name)
    yield tmp_path / TEST_CWL_FP.name  # noqa: PT022


@patch("src.services.ades.factory.current_settings")
def test_ades_client_factory_function_should_create_ades_service_instance(mocked_current_settings: MagicMock) -> None:
    settings = MagicMock()
    mocked_current_settings.return_value = settings
    settings.ades.url = "https://test.ades.com"
    settings.ades.ogc_processes_api_path = "ogc/processes"
    settings.ades.ogc_jobs_api_path = "ogc/jobs"

    result = ades_client_factory(workspace="test", token="test_token")  # noqa: S106

    assert result is not None
    assert result.url == settings.ades.url
    assert result.ogc_jobs_api_path == settings.ades.ogc_jobs_api_path
    assert result.ogc_processes_api_path == settings.ades.ogc_processes_api_path
    assert result.token == "test_token"  # noqa: S105
    assert result.workspace == "test"
    assert result.headers == {
        "Authorization": "Bearer test_token",
        "Accept": "application/json",
    }
    assert result.processes_endpoint_url == "https://test.ades.com/test/ogc/processes"
    assert result.jobs_endpoint_url == "https://test.ades.com/test/ogc/jobs"


@patch("src.services.ades.factory.current_settings")
def test_ades_client_factory_function_should_normalize_workspace_name(mocked_current_settings: MagicMock) -> None:
    settings = MagicMock()
    mocked_current_settings.return_value = settings
    settings.ades.url = "https://test.ades.com"
    settings.ades.ogc_processes_api_path = "ogc/processes"
    settings.ades.ogc_jobs_api_path = "ogc/jobs"

    result = ades_client_factory(workspace="test-WORKSPACE", token="test_token")  # noqa: S106

    assert result is not None
    assert result.url == settings.ades.url
    assert result.ogc_jobs_api_path == settings.ades.ogc_jobs_api_path
    assert result.ogc_processes_api_path == settings.ades.ogc_processes_api_path
    assert result.token == "test_token"  # noqa: S105
    assert result.workspace == "test_workspace"
    assert result.headers == {
        "Authorization": "Bearer test_token",
        "Accept": "application/json",
    }
    assert result.processes_endpoint_url == "https://test.ades.com/test_workspace/ogc/processes"
    assert result.jobs_endpoint_url == "https://test.ades.com/test_workspace/ogc/jobs"


def test_placeholder_replacement(tmp_cwl_file: Path, monkeypatch: MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("SENTINEL_HUB__CLIENT_ID", str(uuid.uuid4()))
    monkeypatch.setenv("SENTINEL_HUB__CLIENT_SECRET", str(uuid.uuid4()))

    # Act
    replace_placeholders_in_cwl_file(tmp_cwl_file)

    # Assert
    # Assert all placeholders have been replaced
    content = tmp_cwl_file.read_text()
    pattern = re.compile(r"<<([A-Za-z\-_ ]+)>>")
    placeholders = re.findall(pattern=pattern, string=content)
    assert not placeholders

    # Assert replaced values match with env vars
    data = yaml.safe_load(
        tmp_cwl_file.open(
            mode="r",
        )
    )
    for node in data["$graph"]:
        if not (requirements := node.get("requirements")):
            continue

        if "EnvVarRequirement" not in requirements:
            continue

        env_vars: dict[str, str] = requirements["EnvVarRequirement"]["envDef"]

        for var_name, var_val in env_vars.items():
            if var_name in {"SENTINEL_HUB__CLIENT_ID", "SENTINEL_HUB__CLIENT_SECRET"}:
                assert var_val == os.environ[var_name]
