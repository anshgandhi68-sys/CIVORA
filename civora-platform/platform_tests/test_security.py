"""Unit tests for Sandbox Security Engine."""

import pytest
from pathlib import Path
from sandbox.security import (
    validate_command_policy,
    check_safe_path,
    redact_credentials,
    validate_safe_url,
)


def test_command_policy_blocks_forbidden_binaries():
    forbidden = ["rm -rf /", "sudo apt-get install", "dd if=/dev/zero of=/dev/sda", "chmod 777 script.sh", "kill -9 1234"]
    for cmd in forbidden:
        allowed, reason = validate_command_policy(cmd)
        assert not allowed, f"Command should be blocked: {cmd}"
        assert reason is not None


def test_command_policy_allows_permitted_binaries():
    permitted = ["python3 -m pytest", "npm test", "pip install -r requirements.txt", "git status", "cargo build"]
    for cmd in permitted:
        allowed, reason = validate_command_policy(cmd)
        assert allowed, f"Command should be allowed: {cmd} (reason: {reason})"


def test_redact_credentials():
    raw = "Here is my secret sk-proj-1234567890abcdef1234567890 and github token ghp_abcdefghijklmnopqr123456"
    redacted = redact_credentials(raw)
    assert "sk-proj-1234567890abcdef1234567890" not in redacted
    assert "ghp_abcdefghijklmnopqr123456" not in redacted
    assert "[REDACTED_CREDENTIAL]" in redacted


def test_safe_path_containment(tmp_path):
    base = tmp_path / "sandbox"
    base.mkdir()
    safe_file = base / "safe.txt"
    safe_file.write_text("hello")

    is_safe, err, res = check_safe_path(base, safe_file)
    assert is_safe
    assert res == safe_file.resolve()

    # Traversal escape
    traversal = base / ".." / "outside.txt"
    is_safe, err, res = check_safe_path(base, traversal)
    assert not is_safe
    assert "escapes sandbox boundary" in err


def test_validate_safe_url():
    assert validate_safe_url("https://github.com/owner/repo.git")
    assert not validate_safe_url("http://127.0.0.1:8000/secret")
    assert not validate_safe_url("http://169.254.169.254/metadata")
