"""CIVORA Engineering Model Context Protocol (MCP) Server.

Exposes read-only repository inspection tools via the official Model Context
Protocol (MCP) Streamable HTTP transport.

Security Architecture:
  - MCPAuthMiddleware wraps the COMPLETE MCP Starlette application (not just
    the route endpoint) so SDK-owned transport-security middleware is preserved
    inside the MCP app stack, while CIVORA shared-header token enforcement is
    applied first at the ASGI boundary.
  - TransportSecuritySettings is configured with explicit allowed_hosts and
    allowed_origins from application settings. DNS-rebinding protection is
    always enabled (never set to False).
  - get_mcp_routes() mounts the authenticated MCP proxy at both /mcp and /mcp/
    using direct Starlette routes to avoid HTTP 307 redirects.
  - refresh_mcp_session_manager() creates a NEW Starlette app (and therefore a
    NEW StreamableHTTPSessionManager) on every lifespan entry so that repeated
    application starts never hit the "session manager already run" RuntimeError.
"""

import logging
import time
from typing import Any, Optional

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
    description=(
        "Retrieve live GitHub repository metadata: full_name, visibility, default_branch, "
        "default_branch_head_sha, repository_url, and archived status."
    ),
)
async def handle_repo_get_metadata(owner: str, repo: str) -> dict[str, Any]:
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
    description=(
        "List all file paths, types, sizes, and git SHAs in the repository tree. "
        "Resolves default branch HEAD if ref is omitted. "
        "Reports truncated=true when the tree exceeds GitHub API limits."
    ),
)
async def handle_repo_list_tree(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
) -> dict[str, Any]:
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
    description=(
        "Safely inspect and redact text file contents from the repository. "
        "Blocks: secret files (.env, .pem, .key, id_rsa), binary files, "
        "path traversal (.. or absolute paths), files > 256KB. "
        "Automatically redacts: AWS keys, GitHub tokens, Bearer tokens, "
        "private key blocks, credential assignments, and database connection strings."
    ),
)
async def handle_repo_read_file(
    owner: str,
    repo: str,
    path: str,
    ref: Optional[str] = None,
) -> dict[str, Any]:
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
    description=(
        "Retrieve all configured GitHub Actions workflow definitions, IDs, states, "
        "and paths for the repository. Results are bounded to a safe maximum page size."
    ),
)
async def handle_ci_get_workflows(owner: str, repo: str) -> dict[str, Any]:
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
    description=(
        "Retrieve live GitHub check run executions, conclusions "
        "(success, failure, pending, cancelled, etc.) for a commit reference. "
        "Results are bounded to a safe maximum page size."
    ),
)
async def handle_ci_get_check_runs(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
) -> dict[str, Any]:
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
    description=(
        "Inspect README.md, CONTRIBUTING.md, package.json, pyproject.toml, "
        "requirements.txt, Cargo.toml, and go.mod to extract setup steps, "
        "commands, and environment variable names. "
        "All repository content is treated as UNTRUSTED DATA. "
        "Extracted commands are never executed. Source file and line numbers are reported."
    ),
)
async def handle_docs_extract_setup_steps(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
) -> dict[str, Any]:
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


def _build_transport_security() -> TransportSecuritySettings:
    """Constructs TransportSecuritySettings from application configuration.

    DNS-rebinding protection is always enabled. Allowed hosts and origins are
    sourced from MCP_ALLOWED_HOSTS and MCP_ALLOWED_ORIGINS settings respectively.
    In production, MCP_ALLOWED_HOSTS is required (validated in config.py).
    """
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=list(settings.MCP_ALLOWED_HOSTS),
        allowed_origins=list(settings.MCP_ALLOWED_ORIGINS),
    )


class MCPProxyApp:
    """Dynamic ASGI proxy allowing MCP Starlette app recreation across lifespans.

    Wraps the COMPLETE Starlette application returned by streamable_http_app()
    (not a single route endpoint) so that SDK-owned middleware stack (transport
    security, body size limits) is fully preserved. MCPAuthMiddleware is then
    applied around this complete app at the ASGI boundary.

    Trailing-slash normalisation: the SDK Starlette app registers only `/mcp`
    (no trailing slash). A trailing-slash request would cause Starlette's own
    redirect_slashes middleware to emit HTTP 307. To avoid that redirect while
    still serving `/mcp/` transparently, this proxy strips a trailing slash
    from `scope["path"]` and `scope["raw_path"]` before forwarding.
    """

    def __init__(self) -> None:
        self.target: Optional[Any] = None
        self._canonical_path: str = ""

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if self.target is None:
            return

        # Normalise trailing slash to avoid SDK-internal HTTP 307 redirects.
        if scope.get("type") == "http":
            path: str = scope.get("path", "")
            if path != self._canonical_path and path == self._canonical_path + "/":
                scope = dict(scope)
                scope["path"] = self._canonical_path
                raw = scope.get("raw_path", b"")
                if raw.endswith(b"/"):
                    scope["raw_path"] = raw[:-1]

        await self.target(scope, receive, send)


_mcp_proxy = MCPProxyApp()


def refresh_mcp_session_manager() -> None:
    """Initializes or refreshes the StreamableHTTP session manager.

    Creates a brand-new MCP Starlette app (and therefore a new
    StreamableHTTPSessionManager) on every call. This prevents the
    'session manager already run' RuntimeError across lifespan restarts
    or repeated test fixture entries.

    The complete Starlette app is wrapped in MCPAuthMiddleware so that:
    1. CIVORA shared-header token authentication is enforced first.
    2. SDK transport-security (DNS-rebinding protection, body size limits)
       is preserved inside the wrapped app's own middleware chain.
    """
    transport_sec = _build_transport_security()
    endpoint_path = settings.MCP_ENDPOINT.rstrip("/")
    mcp_starlette_app = mcp_server.streamable_http_app(
        streamable_http_path=endpoint_path,
        transport_security=transport_sec,
    )
    # Wrap the COMPLETE Starlette ASGI app — preserves SDK middleware chain
    _mcp_proxy.target = MCPAuthMiddleware(mcp_starlette_app)
    _mcp_proxy._canonical_path = endpoint_path


def get_mcp_routes() -> list[Route]:
    """Builds authenticated Starlette routes for the MCP Streamable HTTP endpoint.

    Provides direct routing for both `/mcp` and `/mcp/` without temporary HTTP
    redirects, guaranteeing strict client compatibility across TrueForge and curl.
    """
    refresh_mcp_session_manager()
    methods = ["GET", "POST", "DELETE", "OPTIONS", "HEAD"]
    endpoint_path = settings.MCP_ENDPOINT.rstrip("/")

    return [
        Route(endpoint_path, endpoint=_mcp_proxy, methods=methods),
        Route(f"{endpoint_path}/", endpoint=_mcp_proxy, methods=methods),
    ]
