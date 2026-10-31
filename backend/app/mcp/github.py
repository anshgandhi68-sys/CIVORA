"""GitHub App Authentication Client and Read-Only API Transport."""

import os
import re
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
import httpx
import jwt

from app.core.config import settings

logger = logging.getLogger("civora.mcp.github")

# Safe owner/repo slug validator — prevents injection through repository identifiers
SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+$")

# Safe ref/branch/SHA validator — only alphanumeric, dash, dot, underscore, slash
REF_PATTERN = re.compile(r"^[a-zA-Z0-9_./-]{1,200}$")

# Encoded path traversal detection (catches %2F, %2e%2e, etc.)
ENCODED_TRAVERSAL_PATTERN = re.compile(r"(%2e|%2f|%5c)", re.IGNORECASE)

# Maximum bytes read from GitHub API JSON responses (2 MB)
MAX_RESPONSE_BODY_BYTES = 2 * 1024 * 1024

# Pagination safety limits
MAX_WORKFLOWS_PAGE_SIZE = 100
MAX_CHECK_RUNS_PAGE_SIZE = 100

# In-memory cache for installation tokens: {repo_key: (token, expiry_unix_timestamp)}
_INSTALLATION_TOKEN_CACHE: Dict[str, Tuple[str, float]] = {}


class GitHubAppError(Exception):
    """Base exception for GitHub App operations."""

    def __init__(self, code: str, detail: str, status_code: int = 400) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "detail": self.detail,
            "status_code": self.status_code,
        }


class GitHubAppClient:
    """Read-only GitHub App client utilizing installation-scoped tokens."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        raw_url = (base_url or settings.GITHUB_API_BASE_URL).rstrip("/")
        # Validate HTTPS at construction time to prevent SSRF through injected base_url
        if not raw_url.startswith("https://"):
            raise ValueError(
                f"GitHub API base URL must use HTTPS; got: {raw_url!r}"
            )
        self.base_url = raw_url
        self._http_client = http_client

    def is_configured(self) -> bool:
        """Determines if the minimum GitHub App credentials are set and private key exists."""
        if not settings.GITHUB_APP_ID or not settings.GITHUB_APP_PRIVATE_KEY_PATH:
            return False
        return os.path.exists(settings.GITHUB_APP_PRIVATE_KEY_PATH)

    def _validate_slugs(self, owner: str, repo: str) -> None:
        """Validates repository and owner identifiers to prevent injection attacks."""
        if not owner or not SLUG_PATTERN.match(owner):
            raise GitHubAppError(
                "INVALID_REPOSITORY_OWNER",
                f"Invalid owner format '{owner}'. Must contain only alphanumeric characters, dashes, underscores, or periods.",
                400,
            )
        if not repo or not SLUG_PATTERN.match(repo):
            raise GitHubAppError(
                "INVALID_REPOSITORY_NAME",
                f"Invalid repo format '{repo}'. Must contain only alphanumeric characters, dashes, underscores, or periods.",
                400,
            )

    def _validate_ref(self, ref: str) -> None:
        """Validates branch names, tags, and commit SHAs to prevent header/path injection.

        Allowed: alphanumeric chars, underscore, dash, dot, forward slash.
        Explicitly blocked: '..' sequences (path traversal within refs), null bytes,
        newlines, and other control characters.
        """
        if not ref or not REF_PATTERN.match(ref):
            raise GitHubAppError(
                "INVALID_REF_FORMAT",
                f"Invalid ref format '{ref}'. Must be a valid branch name, tag, or commit SHA.",
                400,
            )
        # Explicitly block '..' sequences regardless of surrounding context
        if ".." in ref:
            raise GitHubAppError(
                "SECURITY_VIOLATION_REF_TRAVERSAL",
                f"Path traversal sequence '..' detected in ref '{ref}'.",
                400,
            )

    def _validate_path(self, path: str) -> None:
        """Validates file paths for encoded path traversal attacks."""
        if ENCODED_TRAVERSAL_PATTERN.search(path):
            raise GitHubAppError(
                "SECURITY_VIOLATION_ENCODED_TRAVERSAL",
                f"Encoded path traversal detected in '{path}'.",
                400,
            )

    def _create_app_jwt(self) -> str:
        """Generates a short-lived RS256 JWT for GitHub App authentication."""
        if not self.is_configured():
            raise GitHubAppError(
                "GITHUB_APP_NOT_CONFIGURED",
                "GitHub App ID or private key path is not configured on this CIVORA instance.",
                503,
            )

        try:
            with open(settings.GITHUB_APP_PRIVATE_KEY_PATH, "r", encoding="utf-8") as f:
                private_key_pem = f.read()
        except Exception as exc:
            logger.error("Failed to read GitHub App private key file: %s", type(exc).__name__)
            raise GitHubAppError(
                "PRIVATE_KEY_READ_ERROR",
                "Unable to load GitHub App private key.",
                500,
            ) from exc

        now = int(time.time())
        payload = {
            "iat": now - 60,  # 60s in the past to compensate for clock drift
            "exp": now + 540,  # 9 minutes expiry (GitHub max 10 min)
            "iss": settings.GITHUB_APP_ID,
        }

        try:
            token = jwt.encode(payload, private_key_pem, algorithm="RS256")
            return token
        except Exception as exc:
            logger.error("Failed to encode GitHub App JWT: %s", type(exc).__name__)
            raise GitHubAppError(
                "JWT_GENERATION_FAILED",
                "Failed to generate GitHub App cryptographic authentication token.",
                500,
            ) from exc

    async def _read_bounded_json(self, resp: httpx.Response) -> Any:
        """Reads and parses a JSON response with an enforced maximum body size.

        Raises GitHubAppError if the response body exceeds MAX_RESPONSE_BODY_BYTES.
        This prevents memory exhaustion from unexpectedly large GitHub API responses.
        """
        content_length = resp.headers.get("content-length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
                if declared_size > MAX_RESPONSE_BODY_BYTES:
                    raise GitHubAppError(
                        "RESPONSE_TOO_LARGE",
                        f"GitHub API response Content-Length ({declared_size} bytes) exceeds "
                        f"the safe maximum ({MAX_RESPONSE_BODY_BYTES} bytes).",
                        502,
                    )
            except ValueError:
                pass

        # Also enforce on actual received body size
        body = resp.content
        if len(body) > MAX_RESPONSE_BODY_BYTES:
            raise GitHubAppError(
                "RESPONSE_TOO_LARGE",
                f"GitHub API response body ({len(body)} bytes) exceeds "
                f"the safe maximum ({MAX_RESPONSE_BODY_BYTES} bytes).",
                502,
            )

        return resp.json()

    async def _get_installation_token(self, owner: str, repo: str, client: httpx.AsyncClient) -> str:
        """Retrieves and caches an installation-scoped token for the given repository."""
        cache_key = f"{owner.lower()}/{repo.lower()}"
        now = time.time()

        if cache_key in _INSTALLATION_TOKEN_CACHE:
            token, expiry = _INSTALLATION_TOKEN_CACHE[cache_key]
            # Use cached token if valid for at least 300 more seconds
            if expiry - now > 300:
                return token

        app_jwt = self._create_app_jwt()
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Step 1: Discover repository installation ID
        inst_url = f"{self.base_url}/repos/{owner}/{repo}/installation"
        try:
            resp = await client.get(inst_url, headers=headers, follow_redirects=False)
        except Exception as exc:
            logger.error("Error communicating with GitHub installation API: %s", type(exc).__name__)
            raise GitHubAppError("GITHUB_API_NETWORK_ERROR", "Network failure connecting to GitHub API.", 502) from exc

        if resp.status_code == 404:
            raise GitHubAppError(
                "GITHUB_APP_NOT_INSTALLED",
                f"CIVORA GitHub App is not installed on repository '{owner}/{repo}'.",
                404,
            )
        if resp.status_code != 200:
            raise GitHubAppError(
                "INSTALLATION_DISCOVERY_FAILED",
                f"GitHub API returned HTTP {resp.status_code} during installation lookup.",
                resp.status_code,
            )

        installation_data = await self._read_bounded_json(resp)
        installation_id = installation_data.get("id")
        if not installation_id:
            raise GitHubAppError(
                "INVALID_INSTALLATION_METADATA",
                "GitHub API response missing installation ID.",
                502,
            )

        # Step 2: Exchange JWT for an installation access token (strict read-only permissions)
        access_token_url = f"{self.base_url}/app/installations/{installation_id}/access_tokens"
        payload = {
            "permissions": {
                "contents": "read",
                "metadata": "read",
                "actions": "read",
                "checks": "read",
            }
        }

        try:
            tok_resp = await client.post(access_token_url, headers=headers, json=payload, follow_redirects=False)
        except Exception as exc:
            raise GitHubAppError("GITHUB_API_NETWORK_ERROR", "Network failure requesting access token.", 502) from exc

        if tok_resp.status_code != 201:
            raise GitHubAppError(
                "INSTALLATION_TOKEN_EXCHANGE_FAILED",
                f"GitHub API returned HTTP {tok_resp.status_code} during token exchange.",
                tok_resp.status_code,
            )

        tok_data = await self._read_bounded_json(tok_resp)
        token = tok_data.get("token")
        expires_at_str = tok_data.get("expires_at")

        if not token:
            raise GitHubAppError("INVALID_TOKEN_RESPONSE", "Access token missing from GitHub response.", 502)

        # Parse expiry timestamp
        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00")).timestamp()
        except Exception:
            expires_at = now + 3600

        _INSTALLATION_TOKEN_CACHE[cache_key] = (token, expires_at)
        return token

    async def request(
        self,
        method: str,
        endpoint: str,
        owner: str,
        repo: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Executes an authenticated read-only request against GitHub REST API."""
        self._validate_slugs(owner, repo)

        # Validate for encoded path traversal in the endpoint string
        self._validate_path(endpoint)

        if not self.is_configured():
            raise GitHubAppError(
                "GITHUB_APP_NOT_CONFIGURED",
                "GitHub App authentication credentials are not configured on this backend.",
                503,
            )

        clean_endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{clean_endpoint}"

        # Guarantee no write HTTP methods are ever dispatched
        if method.upper() not in ["GET", "HEAD"]:
            raise GitHubAppError(
                "READ_ONLY_POLICY_VIOLATION",
                f"HTTP method '{method}' is prohibited. CIVORA Phase 2 engine enforces read-only access.",
                403,
            )

        timeout = httpx.Timeout(15.0, connect=5.0)

        async def _do_req(client: httpx.AsyncClient) -> Any:
            token = await self._get_installation_token(owner, repo, client)
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            resp = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                follow_redirects=False,
            )

            # Check rate limiting headers
            remaining = resp.headers.get("x-ratelimit-remaining")
            if remaining and int(remaining) == 0:
                reset_time = resp.headers.get("x-ratelimit-reset", "unknown")
                raise GitHubAppError(
                    "RATE_LIMIT_EXCEEDED",
                    f"GitHub API rate limit exhausted. Resets at {reset_time}.",
                    429,
                )

            if resp.status_code == 404:
                raise GitHubAppError(
                    "RESOURCE_NOT_FOUND",
                    f"Requested GitHub resource not found at '{endpoint}'.",
                    404,
                )
            if resp.status_code >= 400:
                raise GitHubAppError(
                    "GITHUB_API_ERROR",
                    f"GitHub API returned HTTP {resp.status_code} for '{endpoint}'.",
                    resp.status_code,
                )

            return await self._read_bounded_json(resp)

        if self._http_client is not None:
            return await _do_req(self._http_client)

        async with httpx.AsyncClient(timeout=timeout) as client:
            return await _do_req(client)
