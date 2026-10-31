"""Repository Inspection Tools (Read-Only)."""

import base64
import os
import re
from typing import Any, Dict, List, Optional
from app.mcp.github import GitHubAppClient, GitHubAppError

# Denied sensitive and secret filenames / patterns
DENIED_FILE_PATTERNS = [
    re.compile(r"^\.env(\..+)?$", re.IGNORECASE),
    re.compile(r".*\.pem$", re.IGNORECASE),
    re.compile(r".*\.key$", re.IGNORECASE),
    re.compile(r".*id_rsa.*", re.IGNORECASE),
    re.compile(r".*id_ed25519.*", re.IGNORECASE),
    re.compile(r"credentials(\.json)?$", re.IGNORECASE),
    re.compile(r"secrets(\.json|\.ya?ml)?$", re.IGNORECASE),
]

# Denied binary extensions
DENIED_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".svg",
    ".mp4", ".mov", ".avi", ".mkv", ".webm",
    ".pdf", ".zip", ".tar", ".gz", ".bz2", ".xz", ".whl",
    ".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe", ".bin",
    ".db", ".sqlite", ".sqlite3", ".o", ".a",
}

# Maximum allowable file size to inspect (256 KB)
MAX_FILE_SIZE_BYTES = 256 * 1024

# Secret redaction patterns — ordered from most specific to most general
SECRET_REDACTION_PATTERNS = [
    # AWS Access Key IDs (AKIA prefix, 20 chars total)
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_KEY]"),
    # GitHub personal/oauth/server/refresh/user tokens
    (re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,255}"), "[REDACTED_GITHUB_TOKEN]"),
    # PEM private key blocks (RSA, EC, OpenSSH, PKCS8, PGP)
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"), "[REDACTED_PRIVATE_KEY]"),
    # Bearer / Authorization token header values
    (re.compile(r"(?i)(authorization|bearer)\s*[:\s]+[A-Za-z0-9_\-\.]{20,}"), r"\1: [REDACTED_BEARER_TOKEN]"),
    # Database connection strings with embedded passwords: scheme://user:pass@host
    (re.compile(r"(?i)(postgres(?:ql)?|mysql|mongodb|redis|amqp)://[^:@\s]+:[^@\s]+@"), r"\1://[REDACTED_DB_CREDENTIALS]@"),
    # Unquoted or quoted API_KEY, CLIENT_SECRET, AUTH_TOKEN, PASSWORD assignments
    (re.compile(r"(?i)(api[_-]?key|client[_-]?secret|auth[_-]?token|password)\s*[:=]\s*['\"]?([^'\";\s]{8,})['\"]?"), r"\1=[REDACTED_CREDENTIAL]"),
]


def redact_secrets(content: str) -> str:
    """Sanitizes sensitive secret patterns from file content before returning to caller."""
    redacted = content
    for pattern, replacement in SECRET_REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


async def repo_get_metadata(
    owner: str,
    repo: str,
    client: Optional[GitHubAppClient] = None,
) -> Dict[str, Any]:
    """Retrieves live repository metadata and current default branch commit SHA."""
    gh = client or GitHubAppClient()
    try:
        data = await gh.request("GET", f"repos/{owner}/{repo}", owner, repo)

        default_branch = data.get("default_branch", "main")
        branch_head_sha = "unknown"

        # Resolve head commit SHA for default branch
        try:
            branch_data = await gh.request(
                "GET",
                f"repos/{owner}/{repo}/commits/{default_branch}",
                owner,
                repo,
            )
            branch_head_sha = branch_data.get("sha", "unknown")
        except Exception:
            pass

        return {
            "repository_id": data.get("id"),
            "full_name": data.get("full_name"),
            "visibility": data.get("visibility", "private" if data.get("private") else "public"),
            "default_branch": default_branch,
            "repository_url": data.get("html_url"),
            "default_branch_head_sha": branch_head_sha,
            "archived": data.get("archived", False),
        }
    except GitHubAppError as exc:
        return exc.to_dict()


async def repo_list_tree(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
    client: Optional[GitHubAppClient] = None,
) -> Dict[str, Any]:
    """Retrieves the repository tree at the specified ref, dynamically resolving default HEAD if omitted."""
    gh = client or GitHubAppClient()
    try:
        resolved_ref = ref
        if not resolved_ref:
            meta = await repo_get_metadata(owner, repo, client=gh)
            if "error" in meta:
                return meta
            resolved_ref = meta.get("default_branch_head_sha")
            if not resolved_ref or resolved_ref == "unknown":
                resolved_ref = meta.get("default_branch", "main")

        tree_data = await gh.request(
            "GET",
            f"repos/{owner}/{repo}/git/trees/{resolved_ref}?recursive=1",
            owner,
            repo,
        )

        entries = []
        for item in tree_data.get("tree", []):
            item_type = "file" if item.get("type") == "blob" else ("directory" if item.get("type") == "tree" else item.get("type"))
            entries.append({
                "path": item.get("path"),
                "type": item_type,
                "size": item.get("size"),
                "sha": item.get("sha"),
            })

        return {
            "resolved_ref": resolved_ref,
            "tree": entries,
            "truncated": tree_data.get("truncated", False),
        }
    except GitHubAppError as exc:
        return exc.to_dict()


async def repo_read_file(
    owner: str,
    repo: str,
    path: str,
    ref: Optional[str] = None,
    client: Optional[GitHubAppClient] = None,
) -> Dict[str, Any]:
    """Safely reads and redacts file content from the target repository with zero-trust boundary validation."""
    clean_path = path.strip()

    # 1. Reject absolute paths
    if clean_path.startswith("/") or clean_path.startswith("\\"):
        return {
            "error": "SECURITY_VIOLATION_ABSOLUTE_PATH",
            "detail": f"Absolute paths are forbidden: '{clean_path}'.",
            "status_code": 400,
        }

    # 2. Reject directory traversal
    parts = clean_path.replace("\\", "/").split("/")
    if any(p == ".." for p in parts):
        return {
            "error": "SECURITY_VIOLATION_PATH_TRAVERSAL",
            "detail": f"Path traversal ('..') is strictly prohibited: '{clean_path}'.",
            "status_code": 400,
        }

    filename = os.path.basename(clean_path)
    _, ext = os.path.splitext(filename)

    # 3. Deny known secret / private key files
    for pattern in DENIED_FILE_PATTERNS:
        if pattern.match(filename) or pattern.match(clean_path):
            return {
                "error": "ACCESS_DENIED_SECRET_FILE",
                "detail": f"Access to secret/credential file '{clean_path}' is denied by CIVORA safety policy.",
                "status_code": 403,
            }

    # 4. Reject binary file types
    if ext.lower() in DENIED_BINARY_EXTENSIONS:
        return {
            "error": "BINARY_FILE_REJECTED",
            "detail": f"File extension '{ext}' denotes a binary file, which cannot be inspected via MCP.",
            "status_code": 400,
        }

    gh = client or GitHubAppClient()
    try:
        resolved_ref = ref
        if not resolved_ref:
            meta = await repo_get_metadata(owner, repo, client=gh)
            if "error" in meta:
                return meta
            resolved_ref = meta.get("default_branch_head_sha", "main")

        params = {"ref": resolved_ref}
        file_data = await gh.request(
            "GET",
            f"repos/{owner}/{repo}/contents/{clean_path}",
            owner,
            repo,
            params=params,
        )

        size = file_data.get("size", 0)
        if size > MAX_FILE_SIZE_BYTES:
            return {
                "error": "FILE_TOO_LARGE",
                "detail": f"File size ({size} bytes) exceeds maximum allowable limit of {MAX_FILE_SIZE_BYTES} bytes.",
                "status_code": 413,
            }

        raw_content = file_data.get("content", "")
        encoding = file_data.get("encoding", "base64")

        if encoding == "base64":
            try:
                decoded_bytes = base64.b64decode(raw_content)
                text_content = decoded_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return {
                    "error": "BINARY_CONTENT_DETECTED",
                    "detail": f"File '{clean_path}' contains non-UTF-8 binary data.",
                    "status_code": 400,
                }
        else:
            text_content = raw_content

        redacted_content = redact_secrets(text_content)
        lines = redacted_content.splitlines()

        return {
            "path": clean_path,
            "resolved_ref": resolved_ref,
            "size": size,
            "encoding": "utf-8",
            "line_count": len(lines),
            "content": redacted_content,
        }
    except GitHubAppError as exc:
        return exc.to_dict()
