from __future__ import annotations

from fastapi import FastAPI
from fastapi_hypermodel import (
    HALHyperModel,
)

from src.api.v1_0.routes.action_creator import action_creator_router_v1_0
from src.api.v1_0.routes.auth import auth_router_v1_0
from src.utils.logging import get_logger

_logger = get_logger(__name__)

app = FastAPI(
    title="EOPro Action Creator API",
    version="1.0.0",
    description="Mockup of an API for Action Creator.",
    docs_url=None,
)

v1_0_app = FastAPI(
    title="EOPro Action Creator API", version="1.0.0", description="Mockup of an API for Action Creator."
)
HALHyperModel.init_app(v1_0_app)

v1_0_app.include_router(action_creator_router_v1_0)
v1_0_app.include_router(auth_router_v1_0)

app.mount("/api/v1.0", v1_0_app)
app.mount("/latest", v1_0_app)
