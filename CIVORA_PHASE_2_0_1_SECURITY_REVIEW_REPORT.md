# CIVORA Core — Phase 2.0.1 Security Review & Hardening Report

---

### Executive Summary

Following the initial delivery of Phase 2.0, a rigorous security and implementation audit was conducted on PR #3 (`feat/phase-2-engineering-mcp`). In Phase 2.0.1, all identified vulnerabilities, transport weaknesses, middleware mounting compromises, and documentation inaccuracies have been corrected.

Key hardening outcomes:
1. **MCP DNS-Rebinding Protection Restored**: `enable_dns_rebinding_protection=False` has been completely eradicated. `TransportSecuritySettings` is now explicitly configured with `allowed_hosts` and `allowed_origins` sourced from settings. Disallowed Host headers trigger HTTP 421; disallowed Origin headers trigger HTTP 403.
2. **Complete Starlette ASGI Wrapping**: The complete `Starlette` ASGI application returned by `streamable_http_app()` is now preserved and wrapped by `MCPAuthMiddleware`. Internal route extraction (`routes[0].endpoint`) has been eliminated, preserving SDK transport security and body size limit middlewares while transparently normalizing trailing slashes to prevent HTTP 307 redirects.
3. **GitHub API Transport Hardening**: Strict HTTPS validation is enforced at client initialization. Encoded path traversal (`%2e`, `%2f`, `%5c`) and ref path traversal (`..`) are blocked before request dispatch. Response bodies are bounded to `MAX_RESPONSE_BODY_BYTES = 2MB`, and pagination for workflows and check runs is explicitly bounded to 100 entries.
4. **Expanded Secret Redaction**: Redaction patterns now cover AWS keys, GitHub tokens, PEM private key blocks, Bearer tokens, database connection URIs with passwords (`scheme://user:pass@host`), and both quoted and unquoted `API_KEY` / `CLIENT_SECRET` assignments.
5. **Documentation Alignment**: `backend/README.md` and Phase 2 reports have been aligned with exact code realities. Claims of Markdown AST parsing or RST support have been corrected to reflect the real regex-based code fence extractor with line numbering.
6. **Zero Regressions & Full CI Pass**: Test suite expanded from 41 to 67 unit/security tests (100% green). All 6 GitHub Actions CI checks on commit `d673ead` passed.

---

### 1. Repository Alignment & Git State

| Item | Verified Value |
|:---|:---|
| **Repository URL** | `https://github.com/anshgandhi68-sys/CIVORA.git` |
| **Base Branch & SHA** | `main` @ `5134ae9084415c5c78c28efd3c0fcaaa7063a1a5` |
| **Initial Phase 2.0 PR Commit SHA** | `3ee932c1d31d383b6eb3116ffaf94aea818017c9` |
| **Phase 2.0.1 Hardening Commit SHA** | `d673ead29633e9bfb7fcbcbb7ca3b6e828a2a4b3` |
| **Pull Request** | **[PR #3: feat(mcp): implement real read-only engineering MCP server with Streamable HTTP](https://github.com/anshgandhi68-sys/CIVORA/pull/3)** |
| **Pull Request State** | **OPEN** — 2 commits, +2539 / -18 lines, 6/6 checks passing, 0 merge conflicts |

---

### 2. Detailed Audit Findings & Resolved Issues

#### Finding 1: DNS-Rebinding Protection Shortcut
- **Vulnerability**: `enable_dns_rebinding_protection=False` was passed to `TransportSecuritySettings` in `refresh_mcp_session_manager()`, disabling Host and Origin header validation.
- **Correction**:
  - Removed `enable_dns_rebinding_protection=False`.
  - Added `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS` settings in `backend/app/core/config.py`.
  - In development, defaults allow `localhost`, `localhost:*`, `127.0.0.1`, and `127.0.0.1:*`.
  - In production, `Settings.validate_production_secrets` strictly enforces non-empty `MCP_ALLOWED_HOSTS`, failing closed if missing.
  - Verification: `test_invalid_host_rejected_421` proves unauthorized hosts receive HTTP 421; `test_invalid_origin_rejected_403` proves unauthorized origins receive HTTP 403.

#### Finding 2: Incomplete ASGI Middleware Hierarchy
- **Issue**: `server.py` extracted `raw_endpoint = mcp_starlette_app.routes[0].endpoint` and wrapped only that route endpoint with `MCPAuthMiddleware`. This bypassed Starlette app-level middleware and could compromise SDK lifecycle features.
- **Correction**:
  - `_mcp_proxy.target = MCPAuthMiddleware(mcp_starlette_app)` now wraps the entire Starlette application.
  - Implemented path normalisation in `MCPProxyApp` to strip trailing slashes in ASGI scope (`/mcp/` -> `/mcp`) so the internal Starlette router never issues an HTTP 307 temporary redirect.
  - Session manager recreation remains safe across application reloads via `refresh_mcp_session_manager()`.
  - Verification: `test_mcp_trailing_slash_alias` and `test_mcp_streamable_http_protocol_lifecycle` pass with HTTP 200.

#### Finding 3: GitHub API Transport Vulnerabilities
- **Vulnerabilities**:
  - Potential SSRF if `GITHUB_API_BASE_URL` were configured to an HTTP URL or non-official origin.
  - Potential encoded path traversal (`%2e%2e`, `%2f`).
  - Potential unhandled memory exhaustion from oversized JSON API responses or unbounded lists.
- **Correction**:
  - `GitHubAppClient.__init__` enforces `https://` base URLs at construction time.
  - `Settings` validates `GITHUB_API_BASE_URL` at configuration time, requiring `https://api.github.com` in production.
  - Added `_validate_path()` checking for `%2e`, `%2f`, and `%5c`.
  - Added `_validate_ref()` enforcing regex matching and strictly blocking `..` sequences.
  - Added `_read_bounded_json()` checking `Content-Length` and raw response bytes against `MAX_RESPONSE_BODY_BYTES = 2MB`.
  - Added `MAX_WORKFLOWS_PAGE_SIZE = 100` and `MAX_CHECK_RUNS_PAGE_SIZE = 100` with explicit `bounded_at` metadata in tool responses.
  - Verification: `test_oversized_response_rejected`, `test_encoded_traversal_in_endpoint_rejected`, `test_invalid_ref_format_rejected`, and `test_non_https_base_url_rejected` all pass.

#### Finding 4: Incomplete Secret Redaction
- **Issue**: Database connection strings, Bearer tokens, and unquoted credential assignments were not redacted by the initial regex rules.
- **Correction**:
  - Added regex for Bearer tokens: `(?i)(authorization|bearer)\s*[:\s]+[A-Za-z0-9_\-\.]{20,}`.
  - Added regex for Database connection URIs: `(?i)(postgres(?:ql)?|mysql|mongodb|redis|amqp)://[^:@\s]+:[^@\s]+@`.
  - Added regex for quoted/unquoted credential assignments: `(?i)(api[_-]?key|client[_-]?secret|auth[_-]?token|password)\s*[:=]\s*['"]?([^'";\s]{8,})['"]?`.
  - Verification: 8 targeted unit tests in `TestExpandedSecretRedaction` prove secret values never appear in sanitized output while regular documentation remains unmodified.

#### Finding 5: Documentation & Implementation Discrepancies
- **Discrepancies**:
  - `repo_get_metadata`: Documentation listed `stars, language, topics, permissions` which were not returned. Corrected documentation to list actual fields: `repository_id`, `full_name`, `visibility`, `default_branch`, `default_branch_head_sha`, `repository_url`, `archived`.
  - `repo_list_tree`: Documentation listed `branch?`, `recursive?`. Corrected to actual parameter: `ref?: str`.
  - `docs_extract_setup_steps`: Documentation claimed "Markdown AST parsing" and "RST support". Corrected to state line-based Markdown code fence extractor with classification, source file, and line numbers.
  - Phase 2 Report Commit SHA: Corrected from local placeholder SHA to verified GitHub HEAD SHA `3ee932c1d31d383b6eb3116ffaf94aea818017c9`.

---

### 3. Comprehensive Test Evidence

The backend test suite was expanded from 41 to 67 automated tests:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.18, pytest-9.2.0, pluggy-1.7.0 -- /Users/anshgandhi/CIVORA-AI/backend/.venv/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/anshgandhi/CIVORA-AI/backend
configfile: pyproject.toml
testpaths: tests
plugins: asyncio-1.4.1, anyio-4.15.1
collected 67 items

tests/unit/test_config.py::test_default_settings PASSED                  [  1%]
tests/unit/test_config.py::test_database_url_validation PASSED           [  2%]
tests/unit/test_config.py::test_cors_origins_type PASSED                 [  4%]
tests/unit/test_config.py::test_production_secrets_valid PASSED          [  5%]
tests/unit/test_config.py::test_production_rejects_insecure_default_secret_key PASSED [  7%]
tests/unit/test_config.py::test_production_rejects_short_secret_key PASSED [  8%]
tests/unit/test_config.py::test_production_rejects_insecure_default_mcp_token PASSED [ 10%]
tests/unit/test_config.py::test_production_rejects_short_mcp_token PASSED [ 11%]
tests/unit/test_config.py::test_production_rejects_insecure_default_hmac_secret PASSED [ 13%]
tests/unit/test_config.py::test_production_rejects_short_hmac_secret PASSED [ 14%]
tests/unit/test_config.py::test_production_rejects_missing_secrets PASSED [ 16%]
tests/unit/test_config.py::test_secret_values_never_leak_in_error_messages PASSED [ 17%]
tests/unit/test_health.py::test_health_endpoint PASSED                   [ 19%]
tests/unit/test_health.py::test_readiness_endpoint PASSED                [ 20%]
tests/unit/test_health.py::test_system_info_endpoint PASSED              [ 22%]
tests/unit/test_health.py::test_mcp_server_mounted_read_only PASSED      [ 23%]
tests/unit/test_health.py::test_provenance_enforcement_never_prematurely_active PASSED [ 25%]
tests/unit/test_mcp_auth.py::test_mcp_auth_missing_header_rejected PASSED [ 26%]
tests/unit/test_mcp_auth.py::test_mcp_auth_incorrect_token_rejected PASSED [ 28%]
tests/unit/test_mcp_auth.py::test_mcp_auth_empty_token_rejected PASSED   [ 29%]
tests/unit/test_mcp_auth.py::test_mcp_auth_enforced_across_http_methods PASSED [ 31%]
tests/unit/test_mcp_auth.py::test_mcp_auth_valid_token_accepted PASSED   [ 32%]
tests/unit/test_mcp_github.py::test_github_app_unconfigured PASSED       [ 34%]
tests/unit/test_mcp_github.py::test_github_app_invalid_slugs PASSED      [ 35%]
tests/unit/test_mcp_github.py::test_github_app_jwt_generation PASSED     [ 37%]
tests/unit/test_mcp_github.py::test_github_app_invalid_private_key_file PASSED [ 38%]
tests/unit/test_mcp_github.py::test_installation_token_exchange_and_caching PASSED [ 40%]
tests/unit/test_mcp_github.py::test_read_only_policy_enforcement PASSED  [ 41%]
tests/unit/test_mcp_github.py::test_github_rate_limit_handling PASSED    [ 43%]
tests/unit/test_mcp_security.py::TestHostHeaderValidation::test_valid_host_accepted PASSED [ 44%]
tests/unit/test_mcp_security.py::TestHostHeaderValidation::test_invalid_host_rejected_421 PASSED [ 46%]
tests/unit/test_mcp_security.py::TestHostHeaderValidation::test_invalid_origin_rejected_403 PASSED [ 47%]
tests/unit/test_mcp_security.py::TestMCPTokenAuthentication::test_missing_token_returns_401 PASSED [ 49%]
tests/unit/test_mcp_security.py::TestMCPTokenAuthentication::test_invalid_token_returns_401 PASSED [ 50%]
tests/unit/test_mcp_protocol_flows::TestMCPProtocolFlows::test_initialize_and_tools_list PASSED [ 52%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_non_https_base_url_rejected PASSED [ 53%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_http_base_url_rejected PASSED [ 55%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_https_base_url_accepted PASSED [ 56%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_encoded_traversal_in_endpoint_rejected PASSED [ 58%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_encoded_slash_traversal_rejected PASSED [ 59%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_valid_ref_format_accepted PASSED [ 61%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_invalid_ref_format_rejected PASSED [ 62%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_ref_with_shell_injection_chars_rejected PASSED [ 64%]
tests/unit/test_mcp_security.py::TestGitHubTransportHardening::test_oversized_response_rejected PASSED [ 65%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_aws_key_redacted PASSED [ 67%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_github_token_redacted PASSED [ 68%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_bearer_token_redacted PASSED [ 70%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_private_key_block_redacted PASSED [ 71%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_database_connection_string_redacted PASSED [ 73%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_api_key_assignment_redacted PASSED [ 74%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_client_secret_assignment_redacted PASSED [ 76%]
tests/unit/test_mcp_security.py::TestExpandedSecretRedaction::test_no_false_positives_on_normal_content PASSED [ 77%]
tests/unit/test_mcp_security.py::TestProductionConfigHardening::test_github_api_base_url_must_be_https PASSED [ 79%]
tests/unit/test_mcp_security.py::TestProductionConfigHardening::test_production_requires_mcp_allowed_hosts PASSED [ 80%]
tests/unit/test_mcp_security.py::TestProductionConfigHardening::test_production_requires_official_github_api_url PASSED [ 82%]
tests/unit/test_mcp_server.py::test_mcp_tools_list_discovery PASSED      [ 83%]
tests/unit/test_mcp_server.py::test_mcp_streamable_http_protocol_lifecycle PASSED [ 85%]
tests/unit/test_mcp_server.py::test_mcp_trailing_slash_alias PASSED      [ 86%]
tests/unit/test_mcp_tools.py::test_repo_get_metadata_success PASSED      [ 88%]
tests/unit/test_mcp_tools.py::test_repo_list_tree_and_truncated_detection PASSED [ 89%]
tests/unit/test_mcp_tools.py::test_repo_read_file_security_enforcement PASSED [ 91%]
tests/unit/test_mcp_tools.py::test_repo_read_file_secret_redaction PASSED [ 92%]
tests/unit/test_ci_get_workflows PASSED                                  [ 94%]
tests/unit/test_ci_get_check_runs PASSED                                 [ 95%]
tests/unit/test_docs_extract_setup_steps PASSED                          [ 97%]
tests/unit/test_models.py::test_create_repository PASSED                 [ 98%]
tests/unit/test_models.py::test_create_run_and_relationships PASSED      [100%]

============================== 67 passed in 0.73s ==============================
```

---

### 4. Regression & Verification Matrix

| Validation Stage | Tool / Command | Result |
|:---|:---|:---|
| **Full Unit & Security Tests** | `pytest -v` | **67 passed in 0.73s** |
| **Alembic Schema Upgrade** | `alembic upgrade head` | **Clean on SQLite** |
| **Dependency Integrity** | `pip check` | **No broken requirements** |
| **Production Docker Build** | `docker build` (CI runner) | **Passed in 35s & 48s** |
| **Frontend Production Build** | `tsc && vite build` | **Built in 272ms (100% intact)** |
| **Git Whitespace Audit** | `git diff --check` | **0 errors, 0 warnings** |
| **GitHub Actions PR Checks** | GitHub Actions on `d673ead` | **6/6 checks successful** |

---

### 5. Remaining Limitations

1. **GitHub App Installation Dependency**:
   - The engine gracefully returns structured `GITHUB_APP_NOT_CONFIGURED` when credentials are unset. To perform live repository reads outside of unit tests, a real GitHub App must be registered and its RSA private key mounted on the server.
2. **Single-Page Bounded Lists**:
   - `ci_get_workflows` and `ci_get_check_runs` are intentionally bounded to 100 entries (`bounded_at: 100`). Multi-page cursor pagination is deferred to Phase 3.
3. **Regex-Based Markdown Parsing**:
   - `docs_extract_setup_steps` identifies fenced bash/shell blocks and commands. Nested or non-standard markdown representations without standard code fences are not captured.

---

### 6. Deployment Readiness & GitHub App Configuration Status

- **Container Readiness**: Docker image builds cleanly with non-root user `civora` (UID 1001) and strict `--require-hashes` dependency verification.
- **Environment Guardrails**: Production environment strictly enforces non-default secrets (`SECRET_KEY`, `MCP_AUTH_TOKEN`, `PROVENANCE_HMAC_SECRET`), mandatory `MCP_ALLOWED_HOSTS`, and official `https://api.github.com`.
- **GitHub App Status**: Currently reports `github_integration_status: "unconfigured"` on clean deployments without crashing. Ready for key installation.

---

### 7. Pull Request Status

- **Pull Request**: [anshgandhi68-sys/CIVORA #3](https://github.com/anshgandhi68-sys/CIVORA/pull/3)
- **Base Branch**: `main`
- **Head Branch**: `feat/phase-2-engineering-mcp`
- **Latest Commit**: `d673ead29633e9bfb7fcbcbb7ca3b6e828a2a4b3`
- **Status**: **Open and verified ready for merge review.**
