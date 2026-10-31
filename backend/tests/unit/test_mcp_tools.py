"""Unit Tests for All Six Read-Only MCP Tools."""

from unittest.mock import patch
import base64
import httpx
import pytest

from app.mcp.github import GitHubAppClient, _INSTALLATION_TOKEN_CACHE
from app.mcp.tools.repository import (
    repo_get_metadata,
    repo_list_tree,
    repo_read_file,
    redact_secrets,
)
from app.mcp.tools.ci import (
    ci_get_workflows,
    ci_get_check_runs,
)
from app.mcp.tools.documentation import (
    docs_extract_setup_steps,
)


@pytest.fixture(autouse=True)
def setup_cached_token():
    """Seeds in-memory installation token cache and configures client for mock GitHub API calls."""
    _INSTALLATION_TOKEN_CACHE["testorg/testrepo"] = ("mock-test-token", 9999999999.0)
    with patch("app.mcp.github.GitHubAppClient.is_configured", return_value=True):
        yield



@pytest.mark.asyncio
async def test_repo_get_metadata_success():
    """Verify metadata and dynamic default branch HEAD resolution."""
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith("/repos/testorg/testrepo"):
            return httpx.Response(200, json={
                "id": 123456,
                "full_name": "testorg/testrepo",
                "default_branch": "main",
                "html_url": "https://github.com/testorg/testrepo",
                "private": False,
                "archived": False,
            })
        elif url.endswith("/commits/main"):
            return httpx.Response(200, json={"sha": "abc1234567890def"})
        return httpx.Response(404)

    mock_client = GitHubAppClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    res = await repo_get_metadata("testorg", "testrepo", client=mock_client)

    assert res["repository_id"] == 123456
    assert res["full_name"] == "testorg/testrepo"
    assert res["default_branch"] == "main"
    assert res["default_branch_head_sha"] == "abc1234567890def"
    assert res["visibility"] == "public"


@pytest.mark.asyncio
async def test_repo_list_tree_and_truncated_detection():
    """Verify tree retrieval and truncated tree flag handling."""
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "/commits/main" in url:
            return httpx.Response(200, json={"sha": "commit-sha-999"})
        elif "/git/trees/" in url:
            return httpx.Response(200, json={
                "sha": "tree-sha-999",
                "truncated": True,
                "tree": [
                    {"path": "README.md", "type": "blob", "size": 1024, "sha": "blob-1"},
                    {"path": "src", "type": "tree", "sha": "tree-2"},
                ],
            })
        elif "/repos/testorg/testrepo" in url:
            return httpx.Response(200, json={"default_branch": "main"})
        return httpx.Response(404)

    mock_client = GitHubAppClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    res = await repo_list_tree("testorg", "testrepo", client=mock_client)

    assert res["resolved_ref"] == "commit-sha-999"
    assert res["truncated"] is True
    assert len(res["tree"]) == 2
    assert res["tree"][0]["type"] == "file"
    assert res["tree"][1]["type"] == "directory"


@pytest.mark.asyncio
async def test_repo_read_file_security_enforcement():
    """Verify security controls: path traversal, secrets, and binary extensions blocked."""
    mock_client = GitHubAppClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200))))

    # 1. Absolute path blocked
    r1 = await repo_read_file("testorg", "testrepo", "/etc/passwd", client=mock_client)
    assert r1["error"] == "SECURITY_VIOLATION_ABSOLUTE_PATH"

    # 2. Path traversal blocked
    r2 = await repo_read_file("testorg", "testrepo", "../../config/secret.json", client=mock_client)
    assert r2["error"] == "SECURITY_VIOLATION_PATH_TRAVERSAL"

    # 3. Denied .env file
    r3 = await repo_read_file("testorg", "testrepo", ".env", client=mock_client)
    assert r3["error"] == "ACCESS_DENIED_SECRET_FILE"

    # 4. Denied private key file
    r4 = await repo_read_file("testorg", "testrepo", "server.pem", client=mock_client)
    assert r4["error"] == "ACCESS_DENIED_SECRET_FILE"

    # 5. Denied binary file
    r5 = await repo_read_file("testorg", "testrepo", "logo.png", client=mock_client)
    assert r5["error"] == "BINARY_FILE_REJECTED"


@pytest.mark.asyncio
async def test_repo_read_file_secret_redaction():
    """Verify that file content is read and sensitive keys are redacted."""
    raw_text = (
        "# Setup Instructions\n"
        "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n"
        "GH_TOKEN=ghp_123456789012345678901234567890123456\n"
        "DATABASE_URL=postgres://user:password@localhost/db\n"
    )
    b64_content = base64.b64encode(raw_text.encode("utf-8")).decode("utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "/contents/README.md" in url:
            return httpx.Response(200, json={
                "path": "README.md",
                "size": len(raw_text),
                "encoding": "base64",
                "content": b64_content,
            })
        elif "/repos/testorg/testrepo" in url:
            return httpx.Response(200, json={"default_branch": "main"})
        elif "/commits/main" in url:
            return httpx.Response(200, json={"sha": "sha123"})
        return httpx.Response(404)

    mock_client = GitHubAppClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    res = await repo_read_file("testorg", "testrepo", "README.md", client=mock_client)

    assert res["path"] == "README.md"
    assert "AKIAIOSFODNN7EXAMPLE" not in res["content"]
    assert "[REDACTED_AWS_KEY]" in res["content"]
    assert "ghp_123456789012345678901234567890123456" not in res["content"]
    assert "[REDACTED_GITHUB_TOKEN]" in res["content"]
    assert res["line_count"] == 4


@pytest.mark.asyncio
async def test_ci_get_workflows():
    """Verify CI workflows listing."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "total_count": 1,
            "workflows": [
                {
                    "id": 101,
                    "name": "Backend CI",
                    "path": ".github/workflows/backend-ci.yml",
                    "state": "active",
                    "html_url": "https://github.com/testorg/testrepo/actions/workflows/backend-ci.yml",
                }
            ],
        })

    mock_client = GitHubAppClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    res = await ci_get_workflows("testorg", "testrepo", client=mock_client)

    assert res["total_count"] == 1
    assert res["workflows"][0]["name"] == "Backend CI"
    assert res["workflows"][0]["id"] == 101


@pytest.mark.asyncio
async def test_ci_get_check_runs():
    """Verify check runs retrieval with explicit conclusion statuses."""
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "/check-runs" in url:
            return httpx.Response(200, json={
                "total_count": 2,
                "check_runs": [
                    {
                        "id": 1,
                        "name": "test-suite",
                        "status": "completed",
                        "conclusion": "success",
                        "started_at": "2026-10-31T00:00:00Z",
                        "completed_at": "2026-10-31T00:01:00Z",
                    },
                    {
                        "id": 2,
                        "name": "docker-build",
                        "status": "in_progress",
                        "conclusion": None,
                        "started_at": "2026-10-31T00:01:00Z",
                    },
                ],
            })
        elif "/commits/main" in url:
            return httpx.Response(200, json={"sha": "sha-abc"})
        elif url.rstrip("/").endswith("/repos/testorg/testrepo"):
            return httpx.Response(200, json={"default_branch": "main"})
        return httpx.Response(404)

    mock_client = GitHubAppClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    res = await ci_get_check_runs("testorg", "testrepo", client=mock_client)

    assert res["total_count"] == 2
    assert res["check_runs"][0]["conclusion"] == "success"
    # Unfinished check runs should report "pending"
    assert res["check_runs"][1]["conclusion"] == "pending"


@pytest.mark.asyncio
async def test_docs_extract_setup_steps():
    """Verify setup steps, commands, and environment variables extraction from docs."""
    readme_text = (
        "# Project Onboarding\n"
        "## Setup\n"
        "```bash\n"
        "npm install\n"
        "npm run dev\n"
        "```\n"
        "Environment variables:\n"
        "Requires `DATABASE_URL` and `SECRET_KEY`.\n"
    )
    b64_readme = base64.b64encode(readme_text.encode("utf-8")).decode("utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "/contents/README.md" in url:
            return httpx.Response(200, json={
                "path": "README.md",
                "size": len(readme_text),
                "encoding": "base64",
                "content": b64_readme,
            })
        elif "/git/trees/" in url:
            return httpx.Response(200, json={
                "truncated": False,
                "tree": [{"path": "README.md", "type": "blob", "size": len(readme_text)}],
            })
        elif "/commits/main" in url:
            return httpx.Response(200, json={"sha": "sha-main"})
        elif url.rstrip("/").endswith("/repos/testorg/testrepo"):
            return httpx.Response(200, json={"default_branch": "main"})
        return httpx.Response(404)

    mock_client = GitHubAppClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    res = await docs_extract_setup_steps("testorg", "testrepo", client=mock_client)

    assert "UNTRUSTED DATA" in res["safety_notice"]
    assert "README.md" in res["files_inspected"]
    assert "DATABASE_URL" in res["environment_variables"]
    assert "SECRET_KEY" in res["environment_variables"]
    assert res["extracted_steps_count"] == 2
    assert res["steps"][0]["command"] == "npm install"
    assert res["steps"][0]["category"] == "dependency_install"
    assert res["steps"][1]["command"] == "npm run dev"
    assert res["steps"][1]["category"] == "dev_command"
