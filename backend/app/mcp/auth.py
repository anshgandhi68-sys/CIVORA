"""Zero-Trust Authentication Guard for Model Context Protocol (MCP) Endpoints."""

import hmac
import logging
from typing import Callable
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings

logger = logging.getLogger("civora.mcp.auth")


class MCPAuthMiddleware:
    """ASGI Middleware providing constant-time shared-header token authentication.

    Protects Streamable HTTP MCP endpoints against unauthorized access without
    exposing internal credentials or affecting unauthenticated health probes.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.header_name = settings.MCP_AUTH_HEADER_NAME.lower().encode("latin1")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Fail closed if configured auth token is empty or absent
        expected_token = (settings.MCP_AUTH_TOKEN or "").strip()
        if not expected_token:
            logger.error("MCP authentication rejected: MCP_AUTH_TOKEN is not configured (fail-closed)")
            response = JSONResponse(
                {"error": "Unauthorized: MCP authentication is not configured"},
                status_code=401,
            )
            await response(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        provided_header = headers.get(self.header_name)

        if not provided_header:
            response = JSONResponse(
                {"error": "Unauthorized: Missing authentication header"},
                status_code=401,
            )
            await response(scope, receive, send)
            return

        try:
            provided_token = provided_header.decode("utf-8").strip()
        except UnicodeDecodeError:
            response = JSONResponse(
                {"error": "Unauthorized: Malformed authentication header encoding"},
                status_code=401,
            )
            await response(scope, receive, send)
            return

        if not provided_token:
            response = JSONResponse(
                {"error": "Unauthorized: Empty authentication token"},
                status_code=401,
            )
            await response(scope, receive, send)
            return

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(provided_token, expected_token):
            logger.warning("MCP authentication failed: Invalid token presented")
            response = JSONResponse(
                {"error": "Unauthorized: Invalid authentication token"},
                status_code=401,
            )
            await response(scope, receive, send)
            return

        # Token validated successfully; forward request to MCP ASGI transport
        await self.app(scope, receive, send)
