"""CIVORA Sandbox Execution Manager.

Provides isolated workspace lifecycle management and command execution
under zero-trust safety constraints, timeouts, and credential redaction.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from .security import (
    validate_command_policy,
    check_safe_path,
    redact_credentials,
)


@dataclass
class SandboxExecutionResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool = False
    allowed: bool = True
    rejection_reason: Optional[str] = None
    workspace_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": round(self.duration_ms, 2),
            "timed_out": self.timed_out,
            "allowed": self.allowed,
            "rejection_reason": self.rejection_reason,
            "workspace_path": self.workspace_path,
        }


class SandboxManager:
    """Manages isolated workspaces and executes commands under zero-trust policy."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            self.base_dir = Path("/tmp/civora_sandboxes").resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.active_workspaces: Dict[str, Path] = {}

    def create_workspace(self, workspace_id: Optional[str] = None, source_path: Optional[str] = None) -> Path:
        """Create a new isolated workspace. Optionally clone/copy a source repository."""
        ws_id = workspace_id or f"ws_{uuid.uuid4().hex[:12]}"
        ws_path = (self.base_dir / ws_id).resolve()
        
        # Guard against traversal
        is_safe, err, _ = check_safe_path(self.base_dir, ws_path)
        if not is_safe:
            raise PermissionError(f"Workspace path invalid: {err}")

        if ws_path.exists():
            shutil.rmtree(ws_path, ignore_errors=True)
        ws_path.mkdir(parents=True, exist_ok=True)

        if source_path:
            src = Path(source_path).resolve()
            if src.exists() and src.is_dir():
                # Copy repository contents into the workspace, omitting .git objects or large caches if needed
                for item in src.iterdir():
                    if item.name in {".venv", "node_modules", ".git"}:
                        continue
                    dest = ws_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)

        self.active_workspaces[ws_id] = ws_path
        return ws_path

    def get_workspace(self, workspace_id: str) -> Optional[Path]:
        return self.active_workspaces.get(workspace_id)

    def cleanup_workspace(self, workspace_id: str) -> bool:
        ws_path = self.active_workspaces.pop(workspace_id, None)
        if ws_path and ws_path.exists():
            shutil.rmtree(ws_path, ignore_errors=True)
            return True
        return False

    def execute(
        self,
        command: str,
        workspace_path: Path,
        timeout: int = 30,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> SandboxExecutionResult:
        """Execute command safely inside the isolated workspace."""
        # 1. Zero-trust security policy validation
        is_allowed, reason = validate_command_policy(command)
        if not is_allowed:
            return SandboxExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"[CIVORA ZERO-TRUST REJECTION] {reason}",
                duration_ms=0.0,
                timed_out=False,
                allowed=False,
                rejection_reason=reason,
                workspace_path=str(workspace_path),
            )

        # 2. Workspace path validation
        if not workspace_path.exists():
            return SandboxExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr="[CIVORA ERROR] Workspace directory does not exist.",
                duration_ms=0.0,
                timed_out=False,
                allowed=False,
                rejection_reason="Workspace directory not found",
                workspace_path=str(workspace_path),
            )

        # 3. Environment isolation: retain PATH and essential system vars, add custom env
        safe_env = {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "HOME": str(workspace_path),
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
            "CIVORA_SANDBOX": "1",
        }
        if "PYTHONPATH" in os.environ:
            safe_env["PYTHONPATH"] = os.environ["PYTHONPATH"]
        if env_vars:
            safe_env.update(env_vars)

        start_time = time.perf_counter()
        try:
            process = subprocess.run(
                command,
                cwd=str(workspace_path),
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=safe_env,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            
            clean_stdout = redact_credentials(process.stdout or "")
            clean_stderr = redact_credentials(process.stderr or "")

            return SandboxExecutionResult(
                command=command,
                exit_code=process.returncode,
                stdout=clean_stdout,
                stderr=clean_stderr,
                duration_ms=duration_ms,
                timed_out=False,
                allowed=True,
                workspace_path=str(workspace_path),
            )

        except subprocess.TimeoutExpired as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            raw_stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            raw_stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return SandboxExecutionResult(
                command=command,
                exit_code=124,  # Standard timeout exit code
                stdout=redact_credentials(raw_stdout),
                stderr=f"[CIVORA TIMEOUT] Execution exceeded {timeout}s limit.\n" + redact_credentials(raw_stderr),
                duration_ms=duration_ms,
                timed_out=True,
                allowed=True,
                rejection_reason=f"Timeout after {timeout} seconds",
                workspace_path=str(workspace_path),
            )

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return SandboxExecutionResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr=f"[CIVORA SUBPROCESS ERROR] {str(exc)}",
                duration_ms=duration_ms,
                timed_out=False,
                allowed=True,
                rejection_reason=str(exc),
                workspace_path=str(workspace_path),
            )
