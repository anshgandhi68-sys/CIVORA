"""CIVORA Execution Tools.

Executes permitted development commands, builds, dependency installation,
and test suites safely inside the CIVORA Sandbox.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from sandbox.manager import SandboxManager, SandboxExecutionResult
from .registry import ToolDefinition, ToolParameter, ToolResult

# Shared sandbox manager instance
_sandbox = SandboxManager()


def tool_execute_command(workspace_path: str, command: str, timeout: int = 30) -> ToolResult:
    """Execute permitted command in the isolated workspace."""
    t0 = time.perf_counter()
    try:
        ws_path = Path(workspace_path).resolve()
        res: SandboxExecutionResult = _sandbox.execute(command, ws_path, timeout=timeout)
        duration = (time.perf_counter() - t0) * 1000

        return ToolResult(
            tool_name="execute_command",
            success=(res.exit_code == 0 and res.allowed),
            data={
                "exit_code": res.exit_code,
                "timed_out": res.timed_out,
                "allowed": res.allowed,
                "rejection_reason": res.rejection_reason,
            },
            stdout=res.stdout,
            stderr=res.stderr,
            error=res.rejection_reason if not res.allowed else (res.stderr if res.exit_code != 0 else None),
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("execute_command", False, None, error=str(exc))


def tool_install_dependencies(workspace_path: str, package_manager: str = "auto") -> ToolResult:
    """Install dependencies safely based on manifests."""
    ws_path = Path(workspace_path).resolve()

    # Determine command
    cmd = ""
    pm = package_manager.lower()
    if pm == "auto":
        if (ws_path / "package.json").exists():
            pm = "npm"
        elif (ws_path / "requirements.txt").exists():
            pm = "pip"
        elif (ws_path / "Cargo.toml").exists():
            pm = "cargo"
        else:
            return ToolResult(
                tool_name="install_dependencies",
                success=False,
                data=None,
                error="Could not auto-detect package manager. No manifest found.",
            )

    if pm == "npm":
        cmd = "npm install"
    elif pm == "yarn":
        cmd = "yarn install"
    elif pm == "pnpm":
        cmd = "pnpm install"
    elif pm == "pip":
        cmd = "pip install -r requirements.txt"
    elif pm == "cargo":
        cmd = "cargo build"
    else:
        return ToolResult(
            tool_name="install_dependencies",
            success=False,
            data=None,
            error=f"Unsupported package manager: {package_manager}",
        )

    res = tool_execute_command(workspace_path=str(ws_path), command=cmd, timeout=120)
    res.tool_name = "install_dependencies"
    return res


def tool_run_build(workspace_path: str, command: Optional[str] = None) -> ToolResult:
    """Execute the project build command."""
    ws_path = Path(workspace_path).resolve()
    
    if not command:
        if (ws_path / "package.json").exists():
            command = "npm run build"
        elif (ws_path / "Makefile").exists():
            command = "make build"
        elif (ws_path / "Cargo.toml").exists():
            command = "cargo build --release"
        else:
            command = "npm run build"

    res = tool_execute_command(workspace_path=str(ws_path), command=command, timeout=60)
    res.tool_name = "run_build"
    return res


def tool_run_tests(workspace_path: str, command: Optional[str] = None) -> ToolResult:
    """Execute project test suites."""
    ws_path = Path(workspace_path).resolve()
    
    if not command:
        if (ws_path / "pytest.ini").exists() or any(ws_path.glob("test_*.py")) or (ws_path / "tests").exists():
            command = "pytest"
        elif (ws_path / "package.json").exists():
            command = "npm test"
        elif (ws_path / "Cargo.toml").exists():
            command = "cargo test"
        else:
            command = "pytest"

    res = tool_execute_command(workspace_path=str(ws_path), command=command, timeout=60)
    res.tool_name = "run_tests"
    return res


def tool_inspect_logs(raw_log: str, error_pattern: Optional[str] = None) -> ToolResult:
    """Analyze raw terminal/build logs, extract error lines and stack traces."""
    t0 = time.perf_counter()
    lines = raw_log.splitlines()
    error_lines = []
    stack_traces = []
    in_trace = False
    current_trace = []

    err_regex = re.compile(error_pattern or r"(error|fail|exception|traceback|cannot find module|undefined symbol)", re.IGNORECASE)

    for line in lines:
        if "Traceback (most recent call last):" in line or "Error:" in line:
            in_trace = True
        if in_trace:
            current_trace.append(line)
            if line.strip() == "" and len(current_trace) > 1:
                stack_traces.append("\n".join(current_trace))
                current_trace = []
                in_trace = False
        
        if err_regex.search(line):
            error_lines.append(line.strip())

    if current_trace:
        stack_traces.append("\n".join(current_trace))

    duration = (time.perf_counter() - t0) * 1000
    return ToolResult(
        tool_name="inspect_logs",
        success=True,
        data={
            "total_lines": len(lines),
            "error_count": len(error_lines),
            "error_samples": error_lines[:20],
            "stack_traces": stack_traces[:5],
        },
        execution_time_ms=duration,
    )


def register_execution_tools(registry: Any) -> None:
    """Register all 5 execution tools."""
    registry.register(ToolDefinition(
        name="execute_command",
        category="execution",
        description="Execute a safe developer command in the sandbox (whitelisted binaries only).",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("command", "string", "Permitted shell command to run"),
            ToolParameter("timeout", "integer", "Timeout in seconds", required=False, default=30),
        ],
        handler=tool_execute_command,
    ))

    registry.register(ToolDefinition(
        name="install_dependencies",
        category="execution",
        description="Install dependencies using npm, pip, or cargo in the sandbox.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("package_manager", "string", "auto | npm | pip | cargo", required=False, default="auto"),
        ],
        handler=tool_install_dependencies,
    ))

    registry.register(ToolDefinition(
        name="run_build",
        category="execution",
        description="Run project build command inside the sandbox.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("command", "string", "Custom build command", required=False, default=None),
        ],
        handler=tool_run_build,
    ))

    registry.register(ToolDefinition(
        name="run_tests",
        category="execution",
        description="Run automated tests inside the sandbox.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("command", "string", "Custom test command", required=False, default=None),
        ],
        handler=tool_run_tests,
    ))

    registry.register(ToolDefinition(
        name="inspect_logs",
        category="execution",
        description="Inspect terminal output, diagnose errors and extract stack traces.",
        parameters=[
            ToolParameter("raw_log", "string", "Raw output log text"),
            ToolParameter("error_pattern", "string", "Custom regex pattern", required=False, default=None),
        ],
        handler=tool_inspect_logs,
        requires_sandbox=False,
    ))
