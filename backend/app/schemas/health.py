"""Health and Readiness Pydantic Schemas."""

from datetime import datetime
from typing import Dict, Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    timestamp: datetime
    version: str = "0.1.0"
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready", "degraded", "not_ready"]
    database: Literal["connected", "disconnected", "error"]
    redis: Literal["connected", "disconnected", "disabled"]
    sandbox: str
    details: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime

