"""CIVORA Engineering Model Context Protocol (MCP) Server.

Exposes read-only repository inspection tools via the official Model Context
Protocol (MCP) Streamable HTTP transport.
"""

import logging
import time
from typing import Any, Dict, Optional
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.routing import Route

from app.core.config import settings
from app.mcp.auth import MCPAuthMiddleware
from app.mcp.tools.repository import (
    repo_get_metadata,
    repo_list_tree,
    repo_read_file,
)
from app.mcp.tools.ci import (
    ci_get_workflows,
    ci_get_check_runs,
)
from app.mcp.tools.documentation import (
    docs_extract_setup_steps,
)

logger = logging.getLogger("civora.mcp.server")

# Initialize official MCP v2 Server instance
mcp_server = MCPServer(
    name=settings.MCP_SERVER_NAME,
    version=settings.MCP_SERVER_VERSION,
    instructions="CIVORA Core Engineering Agent Read-Only Repository Inspection Engine",
)


# ==============================================================================
# TOOL 1: repo_get_metadata
# ==============================================================================
@mcp_server.tool(
    name="repo_get_metadata",
    description="Retrieve live GitHub repository metadata, visibility, default branch, and current default branch commit SHA.",
)
async def handle_repo_get_metadata(owner: str, repo: str) -> Dict[str, Any]:
    start = time.time()
    logger.info("MCP tool 'repo_get_metadata' started for repository '%s/%s'", owner, repo)
    try:
        res = await repo_get_metadata(owner, repo)
        elapsed = (time.time() - start) * 1000
        is_success = "error" not in res
        logger.info(
            "MCP tool 'repo_get_metadata' finished in %.2fms (success=%s)",
            elapsed,
            is_success,
        )
        return res
    except Exception as exc:
        elapsed = (time.time() - start) * 1000
        logger.error("MCP tool 'repo_get_metadata' error in %.2fms: %s", elapsed, type(exc).__name__)
        return {
            "error": "INTERNAL_TOOL_ERROR",
            "detail": "Failed to retrieve repository metadata.",
        }


# ==============================================================================
# TOOL 2: repo_list_tree
# ==============================================================================
@mcp_server.tool(
    name="repo_list_tree",
    description="List all file paths, types, sizes, and git SHAs in the repository tree. Resolves default branch HEAD if ref is omitted.",
)
async def handle_repo_list_tree(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
) -> Dict[str, Any]:
    start = time.time()
    logger.info("MCP tool 'repo_list_tree' started for '%s/%s' (ref=%s)", owner, repo, ref or "default")
    try:
        res = await repo_list_tree(owner, repo, ref=ref)
        elapsed = (time.time() - start) * 1000
        is_success = "error" not in res
        logger.info(
            "MCP tool 'repo_list_tree' finished in %.2fms (success=%s, truncated=%s)",
            elapsed,
            is_success,
            res.get("truncated", False),
        )
        return res
    except Exception as exc:
        elapsed = (time.time() - start) * 1000
        logger.error("MCP tool 'repo_list_tree' error in %.2fms: %s", elapsed, type(exc).__name__)
        return {
            "error": "INTERNAL_TOOL_ERROR",
            "detail": "Failed to list repository tree.",
        }


# ==============================================================================
# TOOL 3: repo_read_file
# ==============================================================================
@mcp_server.tool(
    name="repo_read_file",
    description="Safely inspect and redact text file contents from the repository. Blocks secrets, private keys, binaries, and path traversal.",
)
async def handle_repo_read_file(
    owner: str,
    repo: str,
    path: str,
    ref: Optional[str] = None,
) -> Dict[str, Any]:
    start = time.time()
    logger.info("MCP tool 'repo_read_file' started for '%s/%s' path='%s'", owner, repo, path)
    try:
        res = await repo_read_file(owner, repo, path, ref=ref)
        elapsed = (time.time() - start) * 1000
        is_success = "error" not in res
        logger.info("MCP tool 'repo_read_file' finished in %.2fms (success=%s)", elapsed, is_success)
        return res
    except Exception as exc:
        elapsed = (time.time() - start) * 1000
        logger.error("MCP tool 'repo_read_file' error in %.2fms: %s", elapsed, type(exc).__name__)
        return {
            "error": "INTERNAL_TOOL_ERROR",
            "detail": "Failed to read file content.",
        }


# ==============================================================================
# TOOL 4: ci_get_workflows
# ==============================================================================
@mcp_server.tool(
    name="ci_get_workflows",
    description="Retrieve all configured GitHub Actions workflow definitions, IDs, states, and paths for the repository.",
)
async def handle_ci_get_workflows(owner: str, repo: str) -> Dict[str, Any]:
    start = time.time()
    logger.info("MCP tool 'ci_get_workflows' started for '%s/%s'", owner, repo)
    try:
        res = await ci_get_workflows(owner, repo)
        elapsed = (time.time() - start) * 1000
        is_success = "error" not in res
        logger.info("MCP tool 'ci_get_workflows' finished in %.2fms (success=%s)", elapsed, is_success)
        return res
    except Exception as exc:
        elapsed = (time.time() - start) * 1000
        logger.error("MCP tool 'ci_get_workflows' error in %.2fms: %s", elapsed, type(exc).__name__)
        return {
            "error": "INTERNAL_TOOL_ERROR",
            "detail": "Failed to retrieve CI workflows.",
        }


# ==============================================================================
# TOOL 5: ci_get_check_runs
# ==============================================================================
@mcp_server.tool(
    name="ci_get_check_runs",
    description="Retrieve live GitHub check run executions, conclusions (success, failure, pending, cancelled, etc.) for a commit reference.",
)
async def handle_ci_get_check_runs(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
) -> Dict[str, Any]:
    start = time.time()
    logger.info("MCP tool 'ci_get_check_runs' started for '%s/%s' (ref=%s)", owner, repo, ref or "default")
    try:
        res = await ci_get_check_runs(owner, repo, ref=ref)
        elapsed = (time.time() - start) * 1000
        is_success = "error" not in res
        logger.info("MCP tool 'ci_get_check_runs' finished in %.2fms (success=%s)", elapsed, is_success)
        return res
    except Exception as exc:
        elapsed = (time.time() - start) * 1000
        logger.error("MCP tool 'ci_get_check_runs' error in %.2fms: %s", elapsed, type(exc).__name__)
        return {
            "error": "INTERNAL_TOOL_ERROR",
            "detail": "Failed to retrieve check runs.",
        }


# ==============================================================================
# TOOL 6: docs_extract_setup_steps
# ==============================================================================
@mcp_server.tool(
    name="docs_extract_setup_steps",
    description="Inspect README, CONTRIBUTING, package.json, pyproject.toml and extract setup steps, commands, and environment variables. (UNTRUSTED DATA)",
)
async def handle_docs_extract_setup_steps(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
) -> Dict[str, Any]:
    start = time.time()
    logger.info("MCP tool 'docs_extract_setup_steps' started for '%s/%s' (ref=%s)", owner, repo, ref or "default")
    try:
        res = await docs_extract_setup_steps(owner, repo, ref=ref)
        elapsed = (time.time() - start) * 1000
        is_success = "error" not in res
        logger.info(
            "MCP tool 'docs_extract_setup_steps' finished in %.2fms (success=%s, steps=%s)",
            elapsed,
            is_success,
            res.get("extracted_steps_count", 0),
        )
        return res
    except Exception as exc:
        elapsed = (time.time() - start) * 1000
        logger.error("MCP tool 'docs_extract_setup_steps' error in %.2fms: %s", elapsed, type(exc).__name__)
        return {
            "error": "INTERNAL_TOOL_ERROR",
            "detail": "Failed to extract onboarding documentation steps.",
        }


class MCPProxyApp:
    """Dynamic ASGI proxy allowing session manager recreation across lifespans."""

    def __init__(self) -> None:
        self.target: Optional[Any] = None

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if self.target is not None:
            await self.target(scope, receive, send)


_mcp_proxy = MCPProxyApp()


def refresh_mcp_session_manager() -> None:
    """Initializes or refreshes the StreamableHTTP session manager and routes."""
    transport_sec = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    mcp_starlette_app = mcp_server.streamable_http_app(
        streamable_http_path=settings.MCP_ENDPOINT,
        transport_security=transport_sec,
    )
    raw_endpoint = mcp_starlette_app.routes[0].endpoint
    _mcp_proxy.target = MCPAuthMiddleware(raw_endpoint)


def get_mcp_routes() -> list[Route]:
    """Builds authenticated Starlette routes for the MCP Streamable HTTP endpoint.

    Provides direct routing for both `/mcp` and `/mcp/` without temporary HTTP redirects,
    guaranteeing strict client compatibility across TrueForge and curl.
    """
    refresh_mcp_session_manager()
    methods = ["GET", "POST", "DELETE", "OPTIONS", "HEAD"]
    endpoint_path = settings.MCP_ENDPOINT.rstrip("/")

    return [
        Route(endpoint_path, endpoint=_mcp_proxy, methods=methods),
        Route(f"{endpoint_path}/", endpoint=_mcp_proxy, methods=methods),
    ]

