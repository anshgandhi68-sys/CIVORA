"""API Router Configuration."""

from fastapi import APIRouter
from app.api import health, agent

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(agent.router)

