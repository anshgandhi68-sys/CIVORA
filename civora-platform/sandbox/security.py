"""CIVORA Sandbox Security Engine.

Enforces zero-trust command validation, path traversal defense,
credential redaction, and SSRF prevention.
"""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path
from typing import Tuple, List, Set


# Sensitive credential patterns for redaction
CREDENTIAL_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret[_-]?key|token|auth[_-]?token|bearer)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{12,})['\"]?"),
    re.compile(r"sk-[a-zA-Z0-9_\-]{20,}"),
    re.compile(r"ghp_[a-zA-Z0-9]{20,}"),
    re.compile(r"gho_[a-zA-Z0-9]{20,}"),
    re.compile(r"github_pat_[a-zA-Z0-9_]{30,}"),
    re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,}"),
    re.compile(r"https?://([^:]+):([^@]+)@"),  # user:pass in URLs
]

# Strict blacklist of dangerous binaries and primitives
FORBIDDEN_BINARIES: Set[str] = {
    "rm", "unlink", "rmdir", "mkfs", "dd", "fdisk", "parted",
    "chmod", "chown", "chgrp", "sudo", "su", "doas",
    "useradd", "userdel", "usermod", "groupadd", "passwd",
    "shutdown", "reboot", "poweroff", "init", "systemctl",
    "kill", "killall", "pkill",
    "nc", "ncat", "netcat", "socat",
}

# Permitted command prefixes for build/test/repo tasks
PERMITTED_COMMAND_PREFIXES: Set[str] = {
    "node", "npm", "npx", "pnpm", "yarn", "bun",
    "python", "python3", "pip", "pip3", "poetry", "uv", "pipenv", "pytest", "flake8", "mypy", "black", "ruff",
    "git",
    "cargo", "rustc",
    "go",
    "make",
    "ls", "cat", "echo", "pwd", "grep", "find", "wc", "head", "tail", "diff",
    "civora",
}


def redact_credentials(text: str) -> str:
    """Mask sensitive tokens, secrets, and credentials in terminal logs and outputs."""
    if not text:
        return ""
    
    redacted = text
    for pattern in CREDENTIAL_PATTERNS:
        if pattern.groups == 2:
            redacted = pattern.sub(r"\1: [REDACTED_CREDENTIAL]", redacted)
        else:
            redacted = pattern.sub("[REDACTED_CREDENTIAL]", redacted)
    return redacted


def validate_command_policy(command: str) -> Tuple[bool, str]:
    """Inspect and tokenize shell commands against Zero-Trust execution rules.
    
    Rejects:
    - Dangerous binaries (rm, sudo, mkfs, etc.)
    - Direct pipe-to-shell patterns (curl ... | sh, wget ... | bash)
    - Socket redirects (/dev/tcp, /dev/udp)
    - Fork bombs and raw root writes (> /)
    """
    cmd = (command or "").strip()
    if not cmd:
        return False, "Empty command provided."

    # Check for shell piping to interpreter
    pipe_to_shell = re.search(r"\|\s*(ba|z|da|c|k)?sh\b", cmd, re.IGNORECASE)
    if pipe_to_shell:
        return False, "Zero-Trust Policy Violation: Piping remote content directly into a shell interpreter is blocked."

    # Check for raw socket redirection
    if "/dev/tcp" in cmd or "/dev/udp" in cmd:
        return False, "Zero-Trust Policy Violation: Raw network socket redirection is prohibited."

    # Check for fork bombs
    if ":(){ :|:& };:" in cmd or "forkbomb" in cmd.lower():
        return False, "Zero-Trust Policy Violation: Malicious fork bomb pattern detected."

    # Check for root/system directory overwrites
    if re.search(r">\s*/(etc|bin|usr|sbin|boot|lib|sys|proc|var)\b", cmd):
        return False, "Zero-Trust Policy Violation: Writing to host system directories is prohibited."

    # Tokenize command parts safely
    try:
        # Split on common chaining operators to inspect each sub-command
        sub_commands = re.split(r"(?:&&|\|\||;)", cmd)
        for sub in sub_commands:
            sub = sub.strip()
            if not sub:
                continue
            
            tokens = shlex.split(sub)
            if not tokens:
                continue
            
            base_bin = Path(tokens[0]).name.lower()
            
            if base_bin in FORBIDDEN_BINARIES:
                return False, f"Zero-Trust Policy Violation: Binary '{base_bin}' is forbidden in sandbox."

            # Verify binary is in developer toolchain whitelist
            if base_bin not in PERMITTED_COMMAND_PREFIXES:
                return False, f"Zero-Trust Policy Violation: Command '{base_bin}' is not an authorized developer toolchain executable."

    except Exception as e:
        return False, f"Command parsing error: Unable to safely tokenize command ({str(e)})"

    return True, "Authorized"


def validate_safe_path(base_dir: Path | str, target_path: Path | str) -> Path:
    """Enforce strict path containment within the sandbox working directory.
    
    Prevents path traversal attacks (e.g., ../../etc/passwd).
    """
    base = Path(base_dir).resolve()
    target = Path(target_path)
    
    # If target is relative, resolve it relative to base
    if not target.is_absolute():
        resolved = (base / target).resolve()
    else:
        resolved = target.resolve()

    # Check containment
    try:
        resolved.relative_to(base)
    except ValueError:
        raise PermissionError(f"Path traversal detected: '{target_path}' escapes sandbox boundary '{base}'.")

    return resolved


def check_safe_path(base_dir: Path | str, target_path: Path | str) -> Tuple[bool, Optional[str], Optional[Path]]:
    """Helper that returns (is_safe, error_message, resolved_path)."""
    try:
        p = validate_safe_path(base_dir, target_path)
        return True, None, p
    except PermissionError as exc:
        return False, str(exc), None


def validate_safe_url(url: str) -> bool:
    """Validate external repository and documentation URLs for SSRF defense."""
    u = (url or "").strip().lower()
    if not (u.startswith("https://") or u.startswith("http://")):
        return False

    # Block local/internal address schemes
    blocked_hosts = [
        "localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254",
        "::1", "metadata.google.internal"
    ]
    for b in blocked_hosts:
        if f"://{b}" in u or f"@{b}" in u:
            return False

    return True
