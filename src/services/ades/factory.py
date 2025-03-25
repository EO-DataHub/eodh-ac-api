from __future__ import annotations

from src.core.settings import current_settings
from src.services.ades.client import ADESClient
from src.utils.logging import get_logger


def ades_client_factory(workspace: str, token: str) -> ADESClient:
    settings = current_settings()
    workspace = workspace.lower()
    return ADESClient(
        url=settings.ades.url,
        ogc_processes_api_path=settings.ades.ogc_processes_api_path,
        ogc_jobs_api_path=settings.ades.ogc_jobs_api_path,
        workspace=workspace,
        logger=get_logger("ades"),
        token=token,
    )
