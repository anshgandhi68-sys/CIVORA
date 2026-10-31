"""Unit tests for AI Chat Widget endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_chat_endpoint_empty_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "CIVORA AI Engineer" in data["response"]
        assert data["agent"] == "CIVORA TrueFoundry Engineer"


@pytest.mark.asyncio
async def test_chat_endpoint_with_question():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={"message": "Tell me about CI drift detection and zero-trust gate"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "CI-vs-Docs Drift Detection" in data["response"] or "Zero-Trust" in data["response"]


@pytest.mark.asyncio
async def test_chat_endpoint_messages_format():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "What MCP tools are available?"}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "repo_get_metadata" in data["response"]
