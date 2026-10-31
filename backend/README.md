# CIVORA Core — Backend Service

Autonomous Open-Source Onboarding & Documentation Repair Engine Backend.

## Overview
CIVORA Core provides the high-performance backend foundation and Model Context Protocol (MCP) server that empowers the TrueForge CIVORA ENGINEER agent to inspect repositories, diagnose environment setup failures in isolated sandboxes, verify counterfactual fixes, and propose minimal verified documentation pull requests.

## Architecture
- **Framework**: FastAPI (Python 3.13) with asynchronous I/O and Server-Sent Events (SSE).
- **ORM & Database**: SQLAlchemy 2.0 Async + Alembic with dual PostgreSQL (production) and SQLite (development) support.
- **Model Context Protocol**: Official MCP Python SDK v2 (`mcp==2.3.0`) with Streamable HTTP transport at `/mcp`.
- **Engineering Tools**: Six read-only repository inspection tools (`repo_get_metadata`, `repo_list_tree`, `repo_read_file`, `ci_get_workflows`, `ci_get_check_runs`, `docs_extract_setup_steps`).
- **Job Engine**: Asynchronous decoupled job lifecycle (HTTP 202) backed by Redis.
- **Security**: Zero-Trust Provenance Gate restricting patches strictly to `README.md` and `.devcontainer/devcontainer.json`, constant-time MCP authentication (`hmac.compare_digest`), and read-only GitHub App token scoping.

---

## Model Context Protocol (MCP) Architecture

CIVORA Core implements an official MCP server using the MCP Python SDK v2 (`mcp==2.3.0`) mounted directly on the FastAPI ASGI application at `/mcp`.

### 1. Zero-Trust MCP Authentication
Every request reaching `/mcp` is authenticated via a custom header:
- Header Name: `X-CIVORA-MCP-TOKEN` (configurable via `MCP_AUTH_HEADER_NAME`)
- Token: Configured via `MCP_AUTH_TOKEN`
- Verification: Constant-time comparison using `hmac.compare_digest` to eliminate timing side-channel attacks.
- Missing, empty, or mismatched tokens immediately return `401 Unauthorized`.

### 2. Available Read-Only Engineering Tools
CIVORA exposes **strictly read-only** tools for deep repository understanding. No write tools, code execution, or shell execution capabilities exist on the MCP server:

| Tool Name | Parameters | Description |
|:---|:---|:---|
| `repo_get_metadata` | `owner`, `repo` | Fetches repository details, default branch, stars, language, topics, and permissions. |
| `repo_list_tree` | `owner`, `repo`, `branch?`, `recursive?` | Retrieves tree hierarchy (directories and files), reporting `truncated: true` if limits are exceeded. |
| `repo_read_file` | `owner`, `repo`, `path`, `ref?` | Safely reads file contents. Enforces path traversal blocking (`..`, absolute paths), size limits (<=256KB), binary blocking, and automatic secret redaction. |
| `ci_get_workflows` | `owner`, `repo` | Lists GitHub Actions workflows defined in `.github/workflows/`. |
| `ci_get_check_runs` | `owner`, `repo`, `ref?` | Retrieves check runs and suites for a commit or HEAD, classifying statuses (`success`, `failure`, `pending`). |
| `docs_extract_setup_steps` | `owner`, `repo`, `path?` | Parses Markdown/RST documentation files (e.g. `README.md`), identifying setup instructions, code blocks, prerequisites, and line numbers. |

### 3. GitHub App Authentication & Least Privilege
Repository inspection is powered by GitHub App installation tokens:
- **Authentication**: Generates RS256 JWTs signed with the App's private key, resolves repository installation, and exchanges for an installation access token.
- **Caching**: Installation tokens are cached in-memory with automatic TTL expiration (5 minutes buffer before token expiry).
- **Graceful Degradation**: If GitHub App credentials are not configured (`GITHUB_APP_ID` / `GITHUB_APP_PRIVATE_KEY_PATH` unset), tools return a structured `GITHUB_APP_NOT_CONFIGURED` message instead of crashing or leaking exceptions.
- **Required Read-Only Permissions**:
  - `Repository metadata`: Read-only
  - `Repository contents`: Read-only
  - `Actions`: Read-only
  - `Checks`: Read-only

---

## Testing & Agent Integration

### 1. Health & Discovery Probes
Verify system status and MCP server availability:
```bash
curl -s http://localhost:8000/api/v1/system/info | jq .
```
Expected output:
```json
{
  "project_name": "CIVORA Core Backend",
  "version": "0.1.0",
  "environment": "development",
  "mcp_server_available": true,
  "mcp_status": "mounted_read_only",
  "github_integration_available": false,
  "github_integration_status": "unconfigured",
  "provenance_enforced": false
}
```

### 2. MCP JSON-RPC Interaction with curl
List registered MCP tools via Streamable HTTP:
```bash
curl -X POST http://localhost:8000/mcp \
  -H "X-CIVORA-MCP-TOKEN: civora-mcp-local-dev-token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

Call an MCP tool (`repo_get_metadata`):
```bash
curl -X POST http://localhost:8000/mcp \
  -H "X-CIVORA-MCP-TOKEN: civora-mcp-local-dev-token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "repo_get_metadata",
      "arguments": {
        "owner": "anshgandhi68-sys",
        "repo": "CIVORA"
      }
    }
  }'
```

### 3. TrueForge / TrueFoundry Connector Configuration
In TrueFoundry or TrueForge agent configuration:
```yaml
mcpServers:
  civora-engineer:
    url: "http://<civora-backend-host>:8000/mcp"
    transport: "http"
    headers:
      X-CIVORA-MCP-TOKEN: "${CIVORA_MCP_AUTH_TOKEN}"
```

---

---

## Installation & Development Setup

### 1. Prerequisites
- Python 3.13+
- Homebrew (macOS) or build-essential (Linux)

### 2. Environment Initialization
```bash
# Create and activate virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install pip-tools
pip install --upgrade pip pip-tools

# Install development/test dependencies with hash verification
pip install --require-hashes -r requirements-dev.lock

# Or install production runtime-only dependencies
pip install --require-hashes -r requirements-prod.lock
```

### 3. Environment Variables
Copy `.env.example` to `.env` and configure settings:
```bash
cp .env.example .env
```

Key environment configurations:
- `ENVIRONMENT`: `development` (permits local defaults) or `production` (strictly enforces strong secrets).
- `DATABASE_URL`: `sqlite+aiosqlite:///./civora_dev.db` (local) or `postgresql+asyncpg://user:pass@host/db` (prod).
- `SECRET_KEY`: Cryptographic signing key (minimum 32 characters in production).
- `MCP_AUTH_TOKEN`: Bearer token for TrueForge agent connections (minimum 24 characters in production).
- `PROVENANCE_HMAC_SECRET`: HMAC key for patch integrity audits (minimum 32 characters in production).

---

## Database Migrations

Database schemas are managed using Alembic:

```bash
# Apply migrations to the database
alembic upgrade head

# Generate a new migration revision
alembic revision -m "add_new_feature_table"
```

---

## Running the Test Suite

Execute the comprehensive Pytest test suite:

```bash
# Run all unit and integration tests
pytest -v

# Run with test coverage
pytest --cov=app tests/
```

---

## Starting the Service

Launch the FastAPI development server with Uvicorn:

```bash
# Start on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`
- Liveness Probe: `http://localhost:8000/health`
- Readiness Probe: `http://localhost:8000/health/ready`
- System Info: `http://localhost:8000/api/v1/system/info`
