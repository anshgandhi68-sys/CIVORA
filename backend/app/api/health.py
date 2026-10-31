"""Health, Readiness and System Diagnostic Endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthResponse, ReadinessResponse
from app.schemas.system import SystemInfoResponse

router = APIRouter(tags=["Health & System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
)
async def health_check() -> HealthResponse:
    """Returns basic liveness status for orchestration health probes."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        version="0.1.0",
        environment=settings.ENVIRONMENT,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> ReadinessResponse:
    """Verifies database connectivity and infrastructure readiness."""
    db_status = "connected"
    details = {}

    try:
        # Check database connectivity
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = "error"
        details["database_error"] = str(exc)

    redis_status = "disabled"
    if settings.REDIS_ENABLED:
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.REDIS_URL)
            await r.ping()
            await r.close()
            redis_status = "connected"
        except Exception as exc:
            redis_status = "disconnected"
            details["redis_error"] = str(exc)

    overall_status = "ready" if db_status == "connected" else "degraded"

    return ReadinessResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
        sandbox=settings.SANDBOX_BACKEND,
        details=details,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    f"{settings.API_V1_PREFIX}/system/info",
    response_model=SystemInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="System Diagnostic Information",
)
async def system_info() -> SystemInfoResponse:
    """Returns runtime configuration, MCP status and sandbox policy."""
    return SystemInfoResponse(
        project_name=settings.PROJECT_NAME,
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        mcp_endpoint=settings.MCP_ENDPOINT,
        mcp_server_name=settings.MCP_SERVER_NAME,
        allowed_patch_files=settings.ALLOWED_PATCH_FILES,
        sandbox_backend=settings.SANDBOX_BACKEND,
        provenance_enforced=False,
    )

