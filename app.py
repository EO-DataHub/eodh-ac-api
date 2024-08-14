from __future__ import annotations

from fastapi import FastAPI
from fastapi_hypermodel import (
    HALHyperModel,
)

from src.routes.action_creator import router as action_creator_router
from src.utils.logging import get_logger

_logger = get_logger(__name__)
app = FastAPI(title="EODH Action Creator API", version="1.0.0", description="Mockup of an API for Action Creator.")
HALHyperModel.init_app(app)


app.include_router(action_creator_router)
