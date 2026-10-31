"""Integration Tests for MCP Streamable HTTP Server and Tool Discovery."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.core.config import settings
from app.main import app
from app.mcp.server import mcp_server


@pytest.mark.asyncio
async def test_mcp_tools_list_discovery():
    """Verify that all six required read-only tools are registered on the MCP server."""
    tools = await mcp_server.list_tools()
    tool_names = {t.name for t in tools}

    expected_tools = {
        "repo_get_metadata",
        "repo_list_tree",
        "repo_read_file",
        "ci_get_workflows",
        "ci_get_check_runs",
        "docs_extract_setup_steps",
    }

    assert expected_tools.issubset(tool_names), f"Missing tools: {expected_tools - tool_names}"
    assert len(tool_names) == 6, f"Expected exactly 6 read-only tools, found: {tool_names}"


@pytest.mark.asyncio
async def test_mcp_streamable_http_protocol_lifecycle():
    """Verify MCP Streamable HTTP protocol initialization, tool listing, and tool invocation."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            headers = {settings.MCP_AUTH_HEADER_NAME: settings.MCP_AUTH_TOKEN}

            # 1. Initialize
            init_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "trueforge-client", "version": "1.0"},
                },
            }
            res_init = await client.post("/mcp", headers=headers, json=init_payload)
            assert res_init.status_code == 200
            session_id = res_init.headers.get("mcp-session-id")
            assert session_id is not None
            assert "event: message" in res_init.text

            # 2. tools/list over Streamable HTTP
            list_headers = {**headers, "mcp-session-id": session_id}
            list_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
            res_list = await client.post("/mcp", headers=list_headers, json=list_payload)
            assert res_list.status_code == 200
            assert "repo_get_metadata" in res_list.text
            assert "repo_list_tree" in res_list.text
            assert "repo_read_file" in res_list.text
            assert "ci_get_workflows" in res_list.text
            assert "ci_get_check_runs" in res_list.text
            assert "docs_extract_setup_steps" in res_list.text

            # 3. tools/call over Streamable HTTP (calling without credentials returns graceful GITHUB_APP_NOT_CONFIGURED error)
            call_payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "repo_get_metadata",
                    "arguments": {"owner": "testowner", "repo": "testrepo"},
                },
            }
            res_call = await client.post("/mcp", headers=list_headers, json=call_payload)
            assert res_call.status_code == 200
            assert "GITHUB_APP_NOT_CONFIGURED" in res_call.text


@pytest.mark.asyncio
async def test_mcp_trailing_slash_alias():
    """Verify both /mcp and /mcp/ respond with HTTP 200 without HTTP 307 redirect."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            headers = {settings.MCP_AUTH_HEADER_NAME: settings.MCP_AUTH_TOKEN}
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            }
            r1 = await client.post("/mcp", headers=headers, json=payload)
            assert r1.status_code == 200

            r2 = await client.post("/mcp/", headers=headers, json=payload)
            assert r2.status_code == 200
