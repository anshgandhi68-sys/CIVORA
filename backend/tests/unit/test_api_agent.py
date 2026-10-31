"""Unit tests for TrueFoundry Agent API endpoints."""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_agent_status_endpoint():
    """Verify that GET /api/v1/agent/status returns TrueFoundry agent configuration and MCP tools."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/agent/status")
        assert res.status_code == 200
        data = res.json()
        assert data["agent_name"] == "CIVORA ENGINEER"
        assert data["runtime"] == "TrueForge / TrueFoundry Agent"
        assert data["read_only_tools_count"] == 6
        assert "repo_get_metadata" in data["read_only_tools"]
        assert "repo_list_tree" in data["read_only_tools"]
        assert "repo_read_file" in data["read_only_tools"]
        assert "ci_get_workflows" in data["read_only_tools"]
        assert "ci_get_check_runs" in data["read_only_tools"]
        assert "docs_extract_setup_steps" in data["read_only_tools"]


@pytest.mark.asyncio
async def test_agent_inspect_endpoint():
    """Verify that POST /api/v1/agent/inspect executes read-only inspection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.api.agent.repo_get_metadata", new_callable=AsyncMock) as mock_meta, \
             patch("app.api.agent.repo_list_tree", new_callable=AsyncMock) as mock_tree, \
             patch("app.api.agent.docs_extract_setup_steps", new_callable=AsyncMock) as mock_docs, \
             patch("app.api.agent.ci_get_workflows", new_callable=AsyncMock) as mock_wf, \
             patch("app.api.agent.ci_get_check_runs", new_callable=AsyncMock) as mock_cr:

            mock_meta.return_value = {"full_name": "testorg/testrepo", "default_branch": "main"}
            mock_tree.return_value = {"tree": [{"path": "README.md", "type": "file"}]}
            mock_docs.return_value = {"steps": [{"command": "npm install", "line_number": 10}]}
            mock_wf.return_value = {"workflows": [{"name": "CI"}]}
            mock_cr.return_value = {"check_runs": [{"conclusion": "success"}]}

            payload = {"owner": "testorg", "repo": "testrepo", "ref": "main"}
            res = await client.post("/api/v1/agent/inspect", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["owner"] == "testorg"
            assert data["repo"] == "testrepo"
            assert data["metadata"]["full_name"] == "testorg/testrepo"
            assert len(data["docs"]["steps"]) == 1
