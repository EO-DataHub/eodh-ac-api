from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1_0.action_creator.routes import action_creator_router_v1_0
from src.api.v1_0.auth.routes import auth_router_v1_0
from src.api.v1_0.health.routes import health_router_v1_0
from src.api.v1_1.action_creator.routes import action_creator_router_v1_1
from src.api.v1_1.action_creator.ws import action_creator_ws_router_v1_1
from src.api.v1_2.action_creator.routes import action_creator_router_v1_2
from src.api.v1_2.action_creator.ws import action_creator_ws_router_v1_2
from src.api.v1_3.action_creator.routes import action_creator_router_v1_3
from src.api.v1_3.catalogue.routes import catalogue_router_v1_3
from src.core.settings import current_settings

settings = current_settings()


def register_api_v1_0(app: FastAPI) -> FastAPI:
    sub_app = FastAPI(
        title="EOPro Action Creator API [DEPRECATED]",
        version="1.0.0",
        description="API for Action Creator.",
        debug=settings.environment.lower() in {"local", "dev"},
        openapi_url=None if settings.environment.lower() == "prod" else "/openapi.json",
    )
    sub_app.include_router(health_router_v1_0, deprecated=True)
    sub_app.include_router(auth_router_v1_0, deprecated=True)
    sub_app.include_router(action_creator_router_v1_0, deprecated=True)
    app.mount("/api/v1.0", sub_app)
    return sub_app


def register_api_v1_1(app: FastAPI) -> FastAPI:
    sub_app = FastAPI(
        title="EOPro Action Creator API",
        version="1.1.0",
        description="API for Action Creator.",
        debug=settings.environment.lower() in {"local", "dev"},
        openapi_url=None if settings.environment.lower() == "prod" else "/openapi.json",
    )
    sub_app.include_router(health_router_v1_0)
    sub_app.include_router(auth_router_v1_0)
    sub_app.include_router(action_creator_router_v1_1)
    sub_app.include_router(action_creator_ws_router_v1_1, deprecated=True)
    app.mount("/api/v1.1", sub_app)
    return sub_app


def register_api_v1_2(app: FastAPI) -> FastAPI:
    sub_app = FastAPI(
        title="EOPro Action Creator API",
        version="1.2.0",
        description="API for Action Creator.",
        debug=settings.environment.lower() in {"local", "dev"},
        openapi_url=None if settings.environment.lower() == "prod" else "/openapi.json",
    )
    sub_app.include_router(health_router_v1_0)
    sub_app.include_router(auth_router_v1_0)
    sub_app.include_router(action_creator_router_v1_2)
    sub_app.include_router(action_creator_ws_router_v1_2, deprecated=True)
    sub_app.include_router(catalogue_router_v1_3)
    app.mount("/api/v1.2", sub_app)
    return sub_app


def register_api_v1_3(app: FastAPI) -> FastAPI:
    sub_app = FastAPI(
        title="EOPro Action Creator API",
        version="1.3.0",
        description="API for Action Creator.",
        debug=settings.environment.lower() in {"local", "dev"},
        openapi_url=None if settings.environment.lower() == "prod" else "/openapi.json",
    )
    sub_app.include_router(health_router_v1_0)
    sub_app.include_router(auth_router_v1_0)
    sub_app.include_router(action_creator_router_v1_3)
    sub_app.include_router(catalogue_router_v1_3)
    app.mount("/api/v1.3", sub_app)
    return sub_app


app = FastAPI(
    title="EOPro Action Creator API",
    version="1.0.0",
    description="Mockup of an API for Action Creator.",
    docs_url=None,
    debug=True,
)

app_v1_0 = register_api_v1_0(app)
app_v1_1 = register_api_v1_1(app)
app_v1_2 = register_api_v1_2(app)
app_v1_3 = register_api_v1_3(app)
app.mount("/api/latest", app_v1_3)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
