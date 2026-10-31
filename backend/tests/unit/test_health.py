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
    assert data["mcp_server_available"] is True
    assert data["mcp_status"] == "mounted_read_only"
    assert data["github_integration_available"] is False
    assert data["github_integration_status"] == "not_configured"
    assert "README.md" in data["allowed_patch_files"]
    assert data["provenance_enforced"] is False


@pytest.mark.asyncio
async def test_mcp_server_mounted_read_only(async_client: AsyncClient):
    """Verify system info accurately reports MCP server as mounted in read-only mode."""
    response = await async_client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["mcp_server_available"] is True
    assert data["mcp_status"] == "mounted_read_only"
    assert data["github_integration_available"] is False
    assert data["github_integration_status"] == "not_configured"


@pytest.mark.asyncio
async def test_provenance_enforcement_never_prematurely_active(async_client: AsyncClient):
    """Verify system info never reports provenance enforcement active before Phase 6 validator implementation."""
    response = await async_client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert (
        data["provenance_enforced"] is False
    ), "Provenance enforcement must not report True before Phase 6 runtime validator is verified"

