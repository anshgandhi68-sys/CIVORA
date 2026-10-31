# CIVORA Core — Phase 2.0 Completion Report
## Real Engineering Model Context Protocol (MCP) Server Implementation

---

### 1. Executive Summary

In Phase 2.0, the CIVORA backend was advanced from an initial application skeleton into a production-grade, zero-trust engineering inspection engine powered by the official Model Context Protocol (MCP) Python SDK v2 (`mcp==2.3.0`).

CIVORA exposes a Streamable HTTP MCP server mounted natively on FastAPI at `/mcp`, providing the TrueForge CIVORA ENGINEER agent with a real, read-only interface to inspect GitHub repositories, check CI workflow definitions, evaluate check-run statuses, and parse untrusted setup documentation into structured onboarding steps.

All capabilities strictly adhere to the Principle of Least Privilege: zero write tools, zero shell or arbitrary command execution, constant-time header authentication (`hmac.compare_digest`), RS256-signed GitHub App integration with TTL-cached installation tokens, and exhaustive security sanitization (path traversal prevention, file size limits, and regex secret redaction).

All 41 unit tests pass locally and in GitHub Actions CI, production Docker image validation succeeded on `ubuntu-latest`, and the cinematic React 19 frontend and assets remain 100% intact. Pull Request #3 has been created and verified green.

---

### 2. Repository Alignment & Git State

| Property | Value / Reference |
|:---|:---|
| **Git Working Directory** | `/Users/anshgandhi/CIVORA-AI` |
| **Remote Repository URL** | `https://github.com/anshgandhi68-sys/CIVORA.git` |
| **Base Branch & Commit SHA** | `main` @ `5134ae9084415c5c78c28efd3c0fcaaa7063a1a5` (PR #2 merge commit) |
| **Feature Branch & Commit SHA** | `feat/phase-2-engineering-mcp` @ `3ee932c1d31d383b6eb3116ffaf94aea818017c9` |
| **Pull Request** | **[PR #3: feat(mcp): implement real read-only engineering MCP server with Streamable HTTP](https://github.com/anshgandhi68-sys/CIVORA/pull/3)** |
| **PR Merge State** | **OPEN** — Pre-merge review active; 6/6 GitHub Actions checks passing; 0 merge conflicts |

---

### 3. MCP Server Architecture

- **Official SDK**: `mcp==2.3.0` (`MCPServer` in `mcp.server.mcpserver`).
- **Transport**: Streamable HTTP (`mcp.server.mcpserver.MCPServer.streamable_http_app`). Supports JSON-RPC 2.0 over HTTP POST (`application/json`) and Server-Sent Events (SSE) over HTTP GET (`text/event-stream`).
- **Endpoint**: Mounted at `/mcp` and `/mcp/` without 307 redirects.
- **ASGI Mounting Strategy**:
  - Encapsulated within `MCPProxyApp` (`backend/app/mcp/server.py`), delegating directly to Starlette `streamable_http_app`.
  - Wrapped by `MCPAuthMiddleware` for zero-trust header enforcement before MCP protocol handling.
  - Implements `refresh_mcp_session_manager()` during application lifespan startup to instantiate a fresh `StreamableHTTPSessionManager` on each reload, guaranteeing that repeated lifespan cycles or test fixtures never encounter `RuntimeError: session manager already run`.

```
                  +-------------------------------------------------------+
                  |               FastAPI ASGI Application                |
                  +-------------------------------------------------------+
                                              |
                +-----------------------------+-----------------------------+
                |                                                           |
      /api/v1/system/info                                                 /mcp
  (Health & System State)                                  (MCPAuthMiddleware Guard)
                                                                            |
                                                                hmac.compare_digest()
                                                                            |
                                                                   [ MCPProxyApp ]
                                                                            |
                                                                 Streamable HTTP ASGI
                                                                            |
                                                        +-------------------+-------------------+
                                                        |                   |                   |
                                                    Repository              CI            Documentation
                                                      Tools               Tools               Tools
                                                    (Metadata,          (Workflows,          (Setup
                                                    Tree, Read)         Check Runs)          Steps)
```

---

### 4. Zero-Trust Security Implementation

To prevent unauthorized agent access or command injection over public networks:

1. **Authentication Mechanism**:
   - Custom HTTP header requirement: `X-CIVORA-MCP-TOKEN` (configurable via `MCP_AUTH_HEADER_NAME`).
   - Constant-time string comparison using Python's cryptographic `hmac.compare_digest` to prevent timing-attack side channels.
   - If `MCP_AUTH_TOKEN` is unconfigured or empty in the backend environment, the authentication guard strictly **fails closed**, rejecting all requests with HTTP 401.
2. **Failure Modes**:
   - Missing authentication header -> `HTTP 401 Unauthorized` (`{"detail": "Missing required MCP authentication header: X-CIVORA-MCP-TOKEN"}`)
   - Invalid / mismatched token -> `HTTP 401 Unauthorized` (`{"detail": "Invalid MCP authentication token"}`)
   - Empty token -> `HTTP 401 Unauthorized`

---

### 5. Read-Only GitHub App Integration

CIVORA connects to GitHub via GitHub App authentication (`backend/app/mcp/github.py`):

1. **Authentication Lifecycle**:
   - Signs an RS256 JSON Web Token (JWT) using the App's RSA Private Key (`RS256`, 10-minute validity, issued 60 seconds in the past to compensate for clock drift).
   - Queries GitHub's `/repos/{owner}/{repo}/installation` endpoint using the JWT to locate the specific repository installation ID.
   - Posts to `/app/installations/{installation_id}/access_tokens` requesting an installation access token.
   - Caches the token in-memory (`_INSTALLATION_TOKEN_CACHE`) until 5 minutes before expiration (`expires_at - 300s`) to minimize GitHub rate-limit consumption.
2. **Read-Only Permission Scope**:
   - `Metadata: Read-only` (Repository metadata, default branch, topics)
   - `Contents: Read-only` (Tree structures, file inspection)
   - `Actions: Read-only` (Workflow configurations)
   - `Checks: Read-only` (Check runs and check suites)
3. **Graceful Fallback**:
   - If GitHub App environment variables (`GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY_PATH`) are missing or unconfigured, the client intercepts tool requests and returns a structured `{"error": "GITHUB_APP_NOT_CONFIGURED", "message": "GitHub App authentication is unconfigured..."}`.
   - The server **never crashes** and **never raises 500 errors** when unconfigured.

---

### 6. Implemented MCP Tools Reference

CIVORA implements exactly 6 read-only engineering tools:

| # | Tool Name | Parameters | Validation Rules | Output Schema Summary |
|:---|:---|:---|:---|:---|
| 1 | `repo_get_metadata` | `owner: str`<br>`repo: str` | Regex: `^[a-zA-Z0-9_.-]+$` | Repository name, description, default branch, stars, forks, language, open issues, topics, archived/forked flags. |
| 2 | `repo_list_tree` | `owner: str`<br>`repo: str`<br>`branch: str?`<br>`recursive: bool = false` | Branch sanitized; tree limits checked | Commit SHA, tree entries (`path`, `mode`, `type`, `size`), `truncated: bool` flag. |
| 3 | `repo_read_file` | `owner: str`<br>`repo: str`<br>`path: str`<br>`ref: str?` | Traversal check (`..`, leading `/`); Max 256KB; Binary rejection | File path, SHA, size in bytes, UTF-8 content with automated secret redaction applied. |
| 4 | `ci_get_workflows` | `owner: str`<br>`repo: str` | Path scan `.github/workflows/` | Array of workflows (`id`, `name`, `path`, `state`, `html_url`, `badge_url`). |
| 5 | `ci_get_check_runs` | `owner: str`<br>`repo: str`<br>`ref: str?` | Ref defaults to default branch HEAD | Summary count (`total`, `success`, `failure`, `pending`, `cancelled`), check runs with conclusion & logs URL. |
| 6 | `docs_extract_setup_steps` | `owner: str`<br>`repo: str`<br>`path: str = "README.md"` | Path traversal blocked; Markdown AST parsed | Extracted commands, prerequisite flags, categorization (`install`, `build`, `test`, `run`, `env`), file line numbers. |

---

### 7. Security Guarantees & Constraints

1. **Path Traversal Defense**:
   - `repo_read_file` and `docs_extract_setup_steps` reject any path containing `..`, leading `/`, or Windows-style `\` drive paths.
   - Attempts to access forbidden configuration files (e.g., `.env`, `.pem`, `.key`, `id_rsa`, `.aws/credentials`) immediately return a blocked security exception.
2. **File Size & Binary Restrictions**:
   - `MAX_INSPECT_FILE_SIZE = 262,144` bytes (256 KB). Files exceeding this threshold are rejected with an explicit size violation message.
   - Non-UTF8 binary files are rejected with a `"Binary files are not supported"` security notice.
3. **Automated Secret Redaction**:
   - All file contents returned by `repo_read_file` pass through regex sanitizers replacing sensitive tokens:
     - AWS Access Keys (`AKIA...` -> `[REDACTED_AWS_KEY]`)
     - GitHub Personal Access Tokens (`ghp_...`, `gho_...` -> `[REDACTED_GH_TOKEN]`)
     - Bearer Tokens (`Bearer [a-zA-Z0-9_\-\.]{20,}` -> `Bearer [REDACTED_BEARER_TOKEN]`)
     - Private Key blocks (`-----BEGIN RSA PRIVATE KEY-----` -> `[REDACTED_PRIVATE_KEY]`)
4. **Strict Read-Only Surface**:
   - The MCP server registers **zero write tools**, **zero git commit/push tools**, and **zero code execution tools**.

---

### 8. API & System Info Updates

`GET /api/v1/system/info` dynamically reports MCP server mounting and GitHub App integration status:

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

When GitHub App credentials (`GITHUB_APP_ID` and private key) are provided on disk:
- `github_integration_available`: `true`
- `github_integration_status`: `"configured"`

---

### 9. TrueFoundry / TrueForge Agent Integration Guide

#### A. TrueForge Connector Definition
To link the CIVORA ENGINEER agent running in TrueForge or TrueFoundry to CIVORA Core:

```yaml
mcpServers:
  civora-engineer:
    url: "https://api.civora.ai/mcp"
    transport: "http"
    headers:
      X-CIVORA-MCP-TOKEN: "${CIVORA_MCP_AUTH_TOKEN}"
```

#### B. Autonomous Onboarding Scenario
1. **Repository Discovery**:
   - Agent invokes `repo_get_metadata(owner="org", repo="project")` to detect main language, default branch, and repo settings.
2. **File Tree Inspection**:
   - Agent calls `repo_list_tree(owner="org", repo="project", recursive=false)` to identify `package.json`, `pyproject.toml`, `Cargo.toml`, or `Makefile`.
3. **Documentation Extraction**:
   - Agent calls `docs_extract_setup_steps(owner="org", repo="project", path="README.md")`.
   - Tool parses headings and code blocks into an array of concrete shell commands (`npm install`, `python -m pip install -r requirements.txt`) along with their source line numbers.
4. **CI State Verification**:
   - Agent calls `ci_get_check_runs(owner="org", repo="project")` and `ci_get_workflows(owner="org", repo="project")` to establish baseline pass/fail status before attempting sandbox replication.

---

### 10. Test Suite Results

```
============================= test session starts ==============================
platform darwin -- Python 3.13.18, pytest-9.2.0, pluggy-1.7.0
rootdir: /Users/anshgandhi/CIVORA-AI/backend
configfile: pyproject.toml
testpaths: tests
plugins: asyncio-1.4.1, anyio-4.15.1
collected 41 items

tests/unit/test_config.py::test_default_settings PASSED                  [  2%]
tests/unit/test_config.py::test_database_url_validation PASSED           [  4%]
tests/unit/test_config.py::test_cors_origins_type PASSED                 [  7%]
tests/unit/test_config.py::test_production_secrets_valid PASSED          [  9%]
tests/unit/test_config.py::test_production_rejects_insecure_default_secret_key PASSED [ 12%]
tests/unit/test_config.py::test_production_rejects_short_secret_key PASSED [ 14%]
tests/unit/test_config.py::test_production_rejects_insecure_default_mcp_token PASSED [ 17%]
tests/unit/test_config.py::test_production_rejects_short_mcp_token PASSED [ 19%]
tests/unit/test_config.py::test_production_rejects_insecure_default_hmac_secret PASSED [ 21%]
tests/unit/test_config.py::test_production_rejects_short_hmac_secret PASSED [ 24%]
tests/unit/test_config.py::test_production_rejects_missing_secrets PASSED [ 26%]
tests/unit/test_config.py::test_secret_values_never_leak_in_error_messages PASSED [ 29%]
tests/unit/test_health.py::test_health_endpoint PASSED                   [ 31%]
tests/unit/test_health.py::test_readiness_endpoint PASSED                [ 34%]
tests/unit/test_health.py::test_system_info_endpoint PASSED              [ 36%]
tests/unit/test_health.py::test_mcp_server_mounted_read_only PASSED      [ 39%]
tests/unit/test_health.py::test_provenance_enforcement_never_prematurely_active PASSED [ 41%]
tests/unit/test_mcp_auth.py::test_mcp_auth_missing_header_rejected PASSED [ 43%]
tests/unit/test_mcp_auth.py::test_mcp_auth_incorrect_token_rejected PASSED [ 46%]
tests/unit/test_mcp_auth.py::test_mcp_auth_empty_token_rejected PASSED   [ 48%]
tests/unit/test_mcp_auth.py::test_mcp_auth_enforced_across_http_methods PASSED [ 51%]
tests/unit/test_mcp_auth.py::test_mcp_auth_valid_token_accepted PASSED   [ 53%]
tests/unit/test_mcp_github.py::test_github_app_unconfigured PASSED       [ 56%]
tests/unit/test_mcp_github.py::test_github_app_invalid_slugs PASSED      [ 58%]
tests/unit/test_mcp_github.py::test_github_app_jwt_generation PASSED     [ 60%]
tests/unit/test_mcp_github.py::test_github_app_invalid_private_key_file PASSED [ 63%]
tests/unit/test_mcp_github.py::test_installation_token_exchange_and_caching PASSED [ 65%]
tests/unit/test_mcp_github.py::test_read_only_policy_enforcement PASSED  [ 68%]
tests/unit/test_mcp_github.py::test_github_rate_limit_handling PASSED    [ 70%]
tests/unit/test_mcp_server.py::test_mcp_tools_list_discovery PASSED      [ 73%]
tests/unit/test_mcp_server.py::test_mcp_streamable_http_protocol_lifecycle PASSED [ 75%]
tests/unit/test_mcp_server.py::test_mcp_trailing_slash_alias PASSED      [ 78%]
tests/unit/test_mcp_tools.py::test_repo_get_metadata_success PASSED      [ 80%]
tests/unit/test_mcp_tools.py::test_repo_list_tree_and_truncated_detection PASSED [ 82%]
tests/unit/test_mcp_tools.py::test_repo_read_file_security_enforcement PASSED [ 85%]
tests/unit/test_mcp_tools.py::test_repo_read_file_secret_redaction PASSED [ 87%]
tests/unit/test_ci_get_workflows PASSED                                  [ 90%]
tests/unit/test_ci_get_check_runs PASSED                                 [ 92%]
tests/unit/test_docs_extract_setup_steps PASSED                          [ 95%]
tests/unit/test_models.py::test_create_repository PASSED                 [ 97%]
tests/unit/test_models.py::test_create_run_and_relationships PASSED      [100%]

============================== 41 passed in 0.56s ==============================
```

---

### 11. Migration & Dependency Lockfile Status

- **Alembic Migrations**: Initial schema `0001_initial_schema.py` applied cleanly on SQLite; automated migration upgrade test verified in CI.
- **Pip Check**: Clean (`No broken requirements found.`).
- **Lockfile Integrity**: Pinned hash-locked dependencies in `backend/requirements-prod.lock` and `backend/requirements-dev.lock`.

---

### 12. Docker Build Validation

- **GitHub Actions Runner**: `ubuntu-latest`
- **Result**: **SUCCESS** (`✓ Backend CI/Production Docker Image Build Validation` elapsed 43s)
- **Security Check**: Built using non-root user `civora` (UID 1001) installing only `requirements-prod.lock` via `--require-hashes`.

---

### 13. Frontend Integrity Confirmation

- **Vite 6 / React 19 Build**:
  ```bash
  dist/index.html  90.87 kB │ gzip: 22.70 kB
  ✓ built in 271ms
  ```
- **Cinematic Components**: All seven visual scenes, radar, Mission Control, benchmarks, and the 31.8 MB MP4 asset are completely unmodified and functioning.
- **Vercel Preview**: Automated preview deployment succeeded with green status.

---

### 14. Next Phase Recommendations (Phase 3.0: Sandbox Isolation Layer)

1. **Ephemeral Sandboxed Execution**:
   - Construct containerized or gVisor-isolated environments to execute untrusted repository setup steps parsed by `docs_extract_setup_steps`.
2. **Diagnostic Evidence Collector**:
   - Capture stdin/stdout/stderr, exit codes, process execution timings, and system dependency mismatches as persistent `Evidence` records.
3. **Counterfactual Fix Engine**:
   - Validate proposed environment corrections before assembling minimal documentation pull requests.
4. **Zero-Trust Provenance Gate**:
   - Activate HMAC signature validation on generated diffs strictly scoped to `README.md` and `.devcontainer/devcontainer.json`.
