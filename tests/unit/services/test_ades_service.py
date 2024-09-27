from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.services.ades.client import ades_client


@patch("src.services.ades.client.current_settings")
def test_ades_client_factory_function_should_create_ades_service_instance(mocked_current_settings: MagicMock) -> None:
    settings = MagicMock()
    mocked_current_settings.return_value = settings
    settings.ades.url = "https://test.ades.com"
    settings.ades.ogc_processes_api_path = "ogc/processes"
    settings.ades.ogc_jobs_api_path = "ogc/jobs"

    result = ades_client(workspace="test", token="test_token")  # noqa: S106

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
