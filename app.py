from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1_0.action_creator.routes import action_creator_router_v1_0
from src.api.v1_0.auth.routes import auth_router_v1_0
from src.api.v1_0.health.routes import health_router_v1_0
from src.api.v1_1.action_creator.routes import action_creator_router_v1_1

app = FastAPI(
    title="EOPro Action Creator API",
    version="1.0.0",
    description="API for Action Creator.",
    docs_url=None,
)

v1_0_app = FastAPI(title="EOPro Action Creator API", version="1.0.0", description="API for Action Creator.")

v1_1_app = FastAPI(title="EOPro Action Creator API", version="1.1.0", description="API for Action Creator.")

v1_0_app.include_router(health_router_v1_0)
v1_0_app.include_router(auth_router_v1_0)
v1_0_app.include_router(action_creator_router_v1_0)
v1_1_app.include_router(action_creator_router_v1_1)

app.mount("/api/v1.0", v1_0_app)
app.mount("/api/latest", v1_0_app)
app.mount("/api/v1.1", v1_1_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
