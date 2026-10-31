"""Unit Tests for Model Context Protocol (MCP) Authentication Guard."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.core.config import settings
from app.main import app


@pytest.mark.asyncio
async def test_mcp_auth_missing_header_rejected():
    """Verify requests lacking authentication header receive HTTP 401."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            res = await client.post("/mcp", json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1})
            assert res.status_code == 401
            data = res.json()
            assert "Unauthorized" in data.get("error", "")
            # Ensure configured secret is not leaked in error response
            assert settings.MCP_AUTH_TOKEN not in str(data)


@pytest.mark.asyncio
async def test_mcp_auth_incorrect_token_rejected():
    """Verify requests with invalid token receive HTTP 401."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            headers = {settings.MCP_AUTH_HEADER_NAME: "wrong-invalid-token-value"}
            res = await client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1})
            assert res.status_code == 401
            data = res.json()
            assert "Invalid authentication token" in data.get("error", "")
            assert settings.MCP_AUTH_TOKEN not in str(data)


@pytest.mark.asyncio
async def test_mcp_auth_empty_token_rejected():
    """Verify requests with empty token value receive HTTP 401."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            headers = {settings.MCP_AUTH_HEADER_NAME: "   "}
            res = await client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1})
            assert res.status_code == 401


@pytest.mark.asyncio
async def test_mcp_auth_enforced_across_http_methods():
    """Verify authentication is required for POST, GET, and DELETE methods on /mcp."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            r_get = await client.get("/mcp")
            assert r_get.status_code == 401

            r_post = await client.post("/mcp", json={})
            assert r_post.status_code == 401

            r_del = await client.delete("/mcp")
            assert r_del.status_code == 401


@pytest.mark.asyncio
async def test_mcp_auth_valid_token_accepted():
    """Verify requests presenting the correct token are authenticated."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            headers = {settings.MCP_AUTH_HEADER_NAME: settings.MCP_AUTH_TOKEN}
            res = await client.post(
                "/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0"},
                    },
                    "id": 1,
                },
            )
            assert res.status_code == 200
            assert "event: message" in res.text
