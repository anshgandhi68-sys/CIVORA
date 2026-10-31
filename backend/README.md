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

### 1. Zero-Trust MCP Authentication & Transport Security
Every request reaching `/mcp` is authenticated and validated before processing:
- **Header Authentication**: Custom header `X-CIVORA-MCP-TOKEN` (configurable via `MCP_AUTH_HEADER_NAME`).
- **Constant-Time Verification**: Uses `hmac.compare_digest` to prevent timing side-channel attacks.
- **Fail-Closed Policy**: If `MCP_AUTH_TOKEN` is unset or empty, requests immediately return `401 Unauthorized`.
- **DNS-Rebinding Protection**: Transport-level security is enforced via `TransportSecuritySettings`:
  - Host header must match configured `MCP_ALLOWED_HOSTS` (defaults to `["localhost", "localhost:*", "127.0.0.1", "127.0.0.1:*"]`; invalid hosts return `421 Misdirected Request`).
  - Origin header must match configured `MCP_ALLOWED_ORIGINS` (invalid origins return `403 Forbidden`).
  - Production fails closed if `MCP_ALLOWED_HOSTS` is empty.

### 2. Available Read-Only Engineering Tools
CIVORA exposes **strictly read-only** tools for deep repository understanding. No write tools, code execution, or shell execution capabilities exist on the MCP server:

| Tool Name | Parameters | Description |
|:---|:---|:---|
| `repo_get_metadata` | `owner: str`, `repo: str` | Retrieves live metadata: `repository_id`, `full_name`, `visibility`, `default_branch`, `default_branch_head_sha`, `repository_url`, and `archived` status. |
| `repo_list_tree` | `owner: str`, `repo: str`, `ref?: str` | Retrieves full file hierarchy (path, type, size, sha) using recursive tree inspection. Resolves default branch HEAD if `ref` is omitted. Reports `truncated: true` if GitHub limits are reached. |
| `repo_read_file` | `owner: str`, `repo: str`, `path: str`, `ref?: str` | Safely reads text files. Enforces: path traversal (`..`) blocking, forbidden credential files (`.env*`, `*.pem`, `*.key`, `*id_rsa*`), binary extension rejection, file size limit (<=256KB), and automatic redaction of AWS keys, GitHub tokens, Bearer tokens, private keys, database credentials, and API secrets. |
| `ci_get_workflows` | `owner: str`, `repo: str` | Lists GitHub Actions workflows defined under `.github/workflows/`. Results are safely bounded to a maximum of 100 entries (`bounded_at: 100`). |
| `ci_get_check_runs` | `owner: str`, `repo: str`, `ref?: str` | Retrieves check runs and suites for a commit reference (or default branch HEAD), classifying conclusions (`success`, `failure`, `pending`). Results are safely bounded to a maximum of 100 entries (`bounded_at: 100`). |
| `docs_extract_setup_steps` | `owner: str`, `repo: str`, `ref?: str` | Discovers and inspects onboarding files (`README.md`, `CONTRIBUTING.md`, `package.json`, `pyproject.toml`, `requirements.txt`). Extracts shell commands categorized by type (`dependency_install`, `dev_command`, `build_command`, etc.) with exact source line numbers and referenced environment variable names. All extracted data is tagged `UNTRUSTED DATA`. |

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
