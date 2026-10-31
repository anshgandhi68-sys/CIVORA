"""Security Hardening Tests for Phase 2.0.1.

Tests cover:
- Host header validation (DNS-rebinding protection)
- Origin header validation
- MCP token authentication (positive and negative paths)
- MCP Streamable HTTP protocol with valid auth (initialize + tools/list)
- GitHub API transport hardening (HTTPS validation, encoded traversal, response size)
- Expanded secret redaction (bearer tokens, DB connection strings, credential assignments)
- Config production validation (MCP_ALLOWED_HOSTS required, GitHub API URL)
"""

import base64
import httpx
import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient

from app.core.config import settings, Settings
from app.mcp.github import GitHubAppClient, GitHubAppError, _INSTALLATION_TOKEN_CACHE
from app.mcp.tools.repository import redact_secrets
from app.main import app


# ==============================================================================
# 1. HOST HEADER VALIDATION (DNS-Rebinding Protection)
# ==============================================================================

class TestHostHeaderValidation:
    """Verify TransportSecuritySettings Host header enforcement on /mcp."""

    @pytest.mark.asyncio
    async def test_valid_host_accepted(self):
        """Requests with an allowed Host header reach the MCP layer."""
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
                headers = {
                    settings.MCP_AUTH_HEADER_NAME: settings.MCP_AUTH_TOKEN,
                    "Host": "localhost:8000",
                }
                res = await client.post(
                    "/mcp",
                    headers=headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "security-test", "version": "1.0"},
                        },
                    },
                )
                # MCP Auth passes; SDK host validation should also pass for localhost
                assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_invalid_host_rejected_421(self):
        """Requests with a disallowed Host header are rejected HTTP 421 by SDK DNS-rebinding protection."""
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
                headers = {
                    settings.MCP_AUTH_HEADER_NAME: settings.MCP_AUTH_TOKEN,
                    "Host": "evil-attacker.com",
                }
                res = await client.post(
                    "/mcp",
                    headers=headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "attacker", "version": "1.0"},
                        },
                    },
                )
                # SDK transport security returns 421 Misdirected Request for invalid Host
                assert res.status_code == 421

    @pytest.mark.asyncio
    async def test_invalid_origin_rejected_403(self):
        """Requests with a disallowed Origin header are rejected HTTP 403 by SDK DNS-rebinding protection."""
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
                headers = {
                    settings.MCP_AUTH_HEADER_NAME: settings.MCP_AUTH_TOKEN,
                    "Host": "localhost:8000",
                    "Origin": "https://evil-attacker.com",
                }
                res = await client.post(
                    "/mcp",
                    headers=headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "attacker", "version": "1.0"},
                        },
                    },
                )
                # SDK transport security returns 403 Forbidden for invalid Origin
                assert res.status_code == 403


# ==============================================================================
# 2. MCP TOKEN AUTHENTICATION
# ==============================================================================

class TestMCPTokenAuthentication:
    """Verify MCPAuthMiddleware enforces shared-header token authentication."""

    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self):
        """No auth header returns 401."""
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
                res = await client.post("/mcp", json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1})
                assert res.status_code == 401
                body = res.json()
                assert "Unauthorized" in body.get("error", "")
                # Configured secret must not appear in error response
                assert settings.MCP_AUTH_TOKEN not in str(body)

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self):
        """Wrong token returns 401."""
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
                headers = {settings.MCP_AUTH_HEADER_NAME: "wrong-bad-token-value"}
                res = await client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1})
                assert res.status_code == 401
                body = res.json()
                assert settings.MCP_AUTH_TOKEN not in str(body)


# ==============================================================================
# 3. VALID AUTHENTICATED MCP PROTOCOL FLOWS
# ==============================================================================

class TestMCPProtocolFlows:
    """Verify MCP initialize and tools/list succeed with valid auth."""

    @pytest.mark.asyncio
    async def test_initialize_and_tools_list(self):
        """A fully authenticated MCP initialize + tools/list completes successfully."""
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
                auth_headers = {
                    settings.MCP_AUTH_HEADER_NAME: settings.MCP_AUTH_TOKEN,
                    "Host": "localhost:8000",
                }

                # Initialize
                init_res = await client.post(
                    "/mcp",
                    headers=auth_headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "civora-test", "version": "1.0"},
                        },
                    },
                )
                assert init_res.status_code == 200
                session_id = init_res.headers.get("mcp-session-id")
                assert session_id is not None

                # tools/list
                list_res = await client.post(
                    "/mcp",
                    headers={**auth_headers, "mcp-session-id": session_id},
                    json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                )
                assert list_res.status_code == 200
                # Verify all six tools appear
                for tool in [
                    "repo_get_metadata", "repo_list_tree", "repo_read_file",
                    "ci_get_workflows", "ci_get_check_runs", "docs_extract_setup_steps",
                ]:
                    assert tool in list_res.text, f"Tool '{tool}' missing from tools/list response"


# ==============================================================================
# 4. GITHUB TRANSPORT HARDENING
# ==============================================================================

class TestGitHubTransportHardening:
    """Verify GitHub client URL validation, encoded traversal rejection, and response size limits."""

    def test_non_https_base_url_rejected(self):
        """GitHubAppClient constructor rejects non-HTTPS base URLs."""
        with pytest.raises(ValueError, match="must use HTTPS"):
            GitHubAppClient(base_url="http://api.github.com")

    def test_http_base_url_rejected(self):
        """GitHubAppClient constructor rejects plain HTTP."""
        with pytest.raises(ValueError, match="must use HTTPS"):
            GitHubAppClient(base_url="http://evil.com")

    def test_https_base_url_accepted(self):
        """GitHubAppClient accepts HTTPS URL."""
        client = GitHubAppClient(base_url="https://api.github.com")
        assert client.base_url == "https://api.github.com"

    def test_encoded_traversal_in_endpoint_rejected(self):
        """Encoded path traversal (%2e%2e) in endpoint is rejected."""
        client = GitHubAppClient()
        with pytest.raises(GitHubAppError) as exc:
            client._validate_path("repos/org/repo/%2e%2e/secrets")
        assert exc.value.code == "SECURITY_VIOLATION_ENCODED_TRAVERSAL"

    def test_encoded_slash_traversal_rejected(self):
        """Encoded slash (%2f) in endpoint is rejected."""
        client = GitHubAppClient()
        with pytest.raises(GitHubAppError) as exc:
            client._validate_path("repos/org/repo/%2f../../../etc/passwd")
        assert exc.value.code == "SECURITY_VIOLATION_ENCODED_TRAVERSAL"

    def test_valid_ref_format_accepted(self):
        """Valid branch names and SHAs pass validation."""
        client = GitHubAppClient()
        # Should not raise
        client._validate_ref("main")
        client._validate_ref("feature/my-branch")
        client._validate_ref("abc1234567890def")
        client._validate_ref("v1.2.3")

    def test_invalid_ref_format_rejected(self):
        """Refs with '..' traversal or special chars are rejected."""
        client = GitHubAppClient()
        # '..' traversal in refs
        with pytest.raises(GitHubAppError) as exc:
            client._validate_ref("refs/heads/../../evil")
        assert exc.value.code in ("INVALID_REF_FORMAT", "SECURITY_VIOLATION_REF_TRAVERSAL")

    def test_ref_with_shell_injection_chars_rejected(self):
        """Refs containing shell injection characters are rejected."""
        client = GitHubAppClient()
        with pytest.raises(GitHubAppError) as exc:
            client._validate_ref("main;rm -rf /")
        assert exc.value.code == "INVALID_REF_FORMAT"

    @pytest.mark.asyncio
    async def test_oversized_response_rejected(self):
        """Responses exceeding MAX_RESPONSE_BODY_BYTES are rejected with RESPONSE_TOO_LARGE."""
        from app.mcp.github import MAX_RESPONSE_BODY_BYTES
        _INSTALLATION_TOKEN_CACHE["testorg/testrepo"] = ("mock-token", 9999999999.0)

        # Craft a response body larger than the limit
        oversized_body = b"x" * (MAX_RESPONSE_BODY_BYTES + 1)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=oversized_body)

        mock_transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=mock_transport) as http_client:
            client = GitHubAppClient(base_url="https://api.github.com", http_client=http_client)
            with patch("app.mcp.github.GitHubAppClient.is_configured", return_value=True):
                with pytest.raises(GitHubAppError) as exc:
                    await client.request("GET", "repos/testorg/testrepo", "testorg", "testrepo")
                assert exc.value.code == "RESPONSE_TOO_LARGE"


# ==============================================================================
# 5. EXPANDED SECRET REDACTION
# ==============================================================================

class TestExpandedSecretRedaction:
    """Verify all secret patterns are redacted from file content."""

    def test_aws_key_redacted(self):
        content = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\n"
        result = redact_secrets(content)
        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert "[REDACTED_AWS_KEY]" in result

    def test_github_token_redacted(self):
        content = "export GH_TOKEN=ghp_123456789012345678901234567890123456\n"
        result = redact_secrets(content)
        assert "ghp_123456789012345678901234567890123456" not in result
        assert "[REDACTED_GITHUB_TOKEN]" in result

    def test_bearer_token_redacted(self):
        content = "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.abc123\n"
        result = redact_secrets(content)
        # Bearer token value should be redacted
        assert "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.abc123" not in result

    def test_private_key_block_redacted(self):
        content = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----\n"
        result = redact_secrets(content)
        assert "MIIEowIBAAKCAQEA" not in result
        assert "[REDACTED_PRIVATE_KEY]" in result

    def test_database_connection_string_redacted(self):
        content = "DATABASE_URL=postgresql://civora_user:supersecretpassword@db.prod.civora.ai/civora\n"
        result = redact_secrets(content)
        assert "supersecretpassword" not in result
        assert "[REDACTED_DB_CREDENTIALS]" in result

    def test_api_key_assignment_redacted(self):
        content = "api_key=myverysecretapikey12345\n"
        result = redact_secrets(content)
        assert "myverysecretapikey12345" not in result

    def test_client_secret_assignment_redacted(self):
        content = 'CLIENT_SECRET="my-very-long-client-secret-value"\n'
        result = redact_secrets(content)
        assert "my-very-long-client-secret-value" not in result

    def test_no_false_positives_on_normal_content(self):
        """Normal readme content is not incorrectly redacted."""
        content = "# Getting Started\n\nRun `npm install` to set up the project.\n"
        result = redact_secrets(content)
        assert result == content


# ==============================================================================
# 6. PRODUCTION CONFIG HARDENING
# ==============================================================================

class TestProductionConfigHardening:
    """Verify new production validation rules in config."""

    def test_github_api_base_url_must_be_https(self):
        """Non-HTTPS GITHUB_API_BASE_URL is rejected at settings load time."""
        import pydantic
        with pytest.raises((ValueError, pydantic.ValidationError)):
            Settings(
                ENVIRONMENT="development",
                GITHUB_API_BASE_URL="http://api.github.com",
            )

    def test_production_requires_mcp_allowed_hosts(self):
        """Production with empty MCP_ALLOWED_HOSTS raises ValidationError."""
        import pydantic
        with pytest.raises((ValueError, pydantic.ValidationError)):
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="a" * 32,
                MCP_AUTH_TOKEN="a" * 24,
                PROVENANCE_HMAC_SECRET="a" * 32,
                MCP_ALLOWED_HOSTS=[],  # Empty — must be rejected in prod
            )

    def test_production_requires_official_github_api_url(self):
        """Production with non-official GitHub API URL is rejected."""
        import pydantic
        with pytest.raises((ValueError, pydantic.ValidationError)):
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="a" * 32,
                MCP_AUTH_TOKEN="a" * 24,
                PROVENANCE_HMAC_SECRET="a" * 32,
                MCP_ALLOWED_HOSTS=["api.civora.ai"],
                GITHUB_API_BASE_URL="https://github-enterprise.example.com/api/v3",
            )
