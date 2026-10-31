"""Unit Tests for GitHub App Authentication Client and Read-Only Transport."""

import tempfile
import time
from unittest.mock import patch
import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import settings
from app.mcp.github import GitHubAppClient, GitHubAppError, _INSTALLATION_TOKEN_CACHE


@pytest.fixture
def temp_rsa_key_path():
    """Generates a temporary valid 2048-bit RSA private key in PEM format."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with tempfile.NamedTemporaryFile("wb", delete=False) as f:
        f.write(pem)
        f.flush()
        temp_path = f.name

    yield temp_path


def test_github_app_unconfigured():
    """Verify that unconfigured GitHub App safely reports status without raising unhandled errors."""
    client = GitHubAppClient()
    with patch.object(settings, "GITHUB_APP_ID", None):
        assert client.is_configured() is False
        with pytest.raises(GitHubAppError) as exc_info:
            client._create_app_jwt()
        assert exc_info.value.code == "GITHUB_APP_NOT_CONFIGURED"


def test_github_app_invalid_slugs():
    """Verify invalid repository and owner formats are rejected before network calls."""
    client = GitHubAppClient()
    with pytest.raises(GitHubAppError, match="Invalid owner format"):
        client._validate_slugs("owner/invalid", "repo")

    with pytest.raises(GitHubAppError, match="Invalid repo format"):
        client._validate_slugs("owner", "repo;rm -rf /")


def test_github_app_jwt_generation(temp_rsa_key_path):
    """Verify valid RS256 JWT generation using configured credentials."""
    client = GitHubAppClient()
    with patch.object(settings, "GITHUB_APP_ID", "123456"):
        with patch.object(settings, "GITHUB_APP_PRIVATE_KEY_PATH", temp_rsa_key_path):
            assert client.is_configured() is True
            jwt_token = client._create_app_jwt()
            assert isinstance(jwt_token, str)
            assert len(jwt_token) > 100


def test_github_app_invalid_private_key_file():
    """Verify corrupted or invalid private key file raises safe error without leaking details."""
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("corrupted-not-a-private-key")
        f.flush()
        bad_path = f.name

    client = GitHubAppClient()
    with patch.object(settings, "GITHUB_APP_ID", "123456"):
        with patch.object(settings, "GITHUB_APP_PRIVATE_KEY_PATH", bad_path):
            with pytest.raises(GitHubAppError) as exc:
                client._create_app_jwt()
            assert exc.value.code == "JWT_GENERATION_FAILED"


@pytest.mark.asyncio
async def test_installation_token_exchange_and_caching(temp_rsa_key_path):
    """Verify installation token exchange and in-memory caching."""
    _INSTALLATION_TOKEN_CACHE.clear()

    call_counts = {"installation": 0, "access_tokens": 0, "api": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if "/repos/testorg/testrepo/installation" in url_str:
            call_counts["installation"] += 1
            return httpx.Response(200, json={"id": 99999})
        elif "/app/installations/99999/access_tokens" in url_str:
            call_counts["access_tokens"] += 1
            return httpx.Response(201, json={"token": "ghs_testtoken12345", "expires_at": "2030-01-01T00:00:00Z"})
        elif "/repos/testorg/testrepo" in url_str:
            call_counts["api"] += 1
            return httpx.Response(200, json={"id": 1, "name": "testrepo", "default_branch": "main"})
        return httpx.Response(404, json={"message": "Not Found"})

    mock_transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = GitHubAppClient(base_url="https://api.github.com", http_client=http_client)

        with patch.object(settings, "GITHUB_APP_ID", "123456"):
            with patch.object(settings, "GITHUB_APP_PRIVATE_KEY_PATH", temp_rsa_key_path):
                # Call 1: Should fetch installation & token, then make request
                res1 = await client.request("GET", "repos/testorg/testrepo", "testorg", "testrepo")
                assert res1["name"] == "testrepo"
                assert call_counts["installation"] == 1
                assert call_counts["access_tokens"] == 1
                assert call_counts["api"] == 1

                # Call 2: Should use cached installation token!
                res2 = await client.request("GET", "repos/testorg/testrepo", "testorg", "testrepo")
                assert res2["name"] == "testrepo"
                assert call_counts["installation"] == 1
                assert call_counts["access_tokens"] == 1
                assert call_counts["api"] == 2


@pytest.mark.asyncio
async def test_read_only_policy_enforcement(temp_rsa_key_path):
    """Verify non-read-only HTTP methods (POST, PUT, DELETE, PATCH) are blocked by client policy."""
    client = GitHubAppClient()
    with patch.object(settings, "GITHUB_APP_ID", "123456"):
        with patch.object(settings, "GITHUB_APP_PRIVATE_KEY_PATH", temp_rsa_key_path):
            with pytest.raises(GitHubAppError) as exc:
                await client.request("POST", "repos/testorg/testrepo/issues", "testorg", "testrepo")
            assert exc.value.code == "READ_ONLY_POLICY_VIOLATION"


@pytest.mark.asyncio
async def test_github_rate_limit_handling(temp_rsa_key_path):
    """Verify rate limit response header triggers structured RATE_LIMIT_EXCEEDED error."""
    _INSTALLATION_TOKEN_CACHE["testorg/testrepo"] = ("token", time.time() + 3600)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1730000000"},
            json={"message": "API rate limit exceeded"},
        )

    mock_transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = GitHubAppClient(http_client=http_client)
        with patch.object(settings, "GITHUB_APP_ID", "123456"):
            with patch.object(settings, "GITHUB_APP_PRIVATE_KEY_PATH", temp_rsa_key_path):
                with pytest.raises(GitHubAppError) as exc:
                    await client.request("GET", "repos/testorg/testrepo", "testorg", "testrepo")
                assert exc.value.code == "RATE_LIMIT_EXCEEDED"
