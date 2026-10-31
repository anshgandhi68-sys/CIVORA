"""Integration Tests for Health and System Endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    """Verify GET /health returns 200 OK and valid schema."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-MS" in response.headers


@pytest.mark.asyncio
async def test_readiness_endpoint(async_client: AsyncClient):
    """Verify GET /health/ready returns 200 OK and connected database."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ready", "degraded"]
    assert data["database"] == "connected"
    assert "sandbox" in data


@pytest.mark.asyncio
async def test_system_info_endpoint(async_client: AsyncClient):
    """Verify GET /api/v1/system/info returns configuration metadata."""
    response = await async_client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "CIVORA Core Backend"
    assert data["mcp_endpoint"] == "/mcp"
    assert data["mcp_server_name"] == "civora-engineer"
    assert data["mcp_server_available"] is False
    assert data["mcp_status"] == "not_mounted"
    assert "README.md" in data["allowed_patch_files"]
    assert data["provenance_enforced"] is False


@pytest.mark.asyncio
async def test_mcp_server_never_prematurely_available(async_client: AsyncClient):
    """Verify system info never reports MCP server as available before Phase 2 registration."""
    response = await async_client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert (
        data["mcp_server_available"] is False
    ), "MCP server must not report True before Phase 2 endpoint registration"
    assert data["mcp_status"] == "not_mounted"


@pytest.mark.asyncio
async def test_provenance_enforcement_never_prematurely_active(async_client: AsyncClient):
    """Verify system info never reports provenance enforcement active before Phase 6 validator implementation."""
    response = await async_client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert (
        data["provenance_enforced"] is False
    ), "Provenance enforcement must not report True before Phase 6 runtime validator is verified"

