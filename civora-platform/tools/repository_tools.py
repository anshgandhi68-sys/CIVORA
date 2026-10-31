"""CIVORA Repository Analysis Tools.

Provides safe inspection of repository files, code search, dependency manifests,
configuration files, and git history within the sandbox boundary.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from sandbox.security import check_safe_path, redact_credentials
from .registry import ToolDefinition, ToolParameter, ToolResult


def tool_list_files(workspace_path: str, subpath: str = ".", max_depth: int = 3) -> ToolResult:
    """List directory tree up to max_depth."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        target = (base / subpath).resolve()
        is_safe, err, _ = check_safe_path(base, target)
        if not is_safe:
            return ToolResult("list_files", False, None, error=f"Path security violation: {err}")

        if not target.exists():
            return ToolResult("list_files", False, None, error=f"Target path does not exist: {subpath}")

        entries = []
        target_depth = len(target.parts)
        for root, dirs, files in os.walk(target):
            # prune hidden and heavy cache directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".venv")]
            curr_depth = len(Path(root).parts) - target_depth
            if curr_depth > max_depth:
                continue

            rel_root = os.path.relpath(root, base)
            for f in files:
                if f.startswith("."):
                    continue
                entries.append(os.path.normpath(os.path.join(rel_root, f)))

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="list_files",
            success=True,
            data={"files": sorted(entries), "total_count": len(entries)},
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("list_files", False, None, error=str(exc))


def tool_read_file(workspace_path: str, file_path: str, start_line: int = 1, end_line: int = 500) -> ToolResult:
    """Read a specific range of lines from a safe file."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        target = (base / file_path).resolve()
        is_safe, err, _ = check_safe_path(base, target)
        if not is_safe:
            return ToolResult("read_file", False, None, error=f"Path violation: {err}")

        if not target.exists() or not target.is_file():
            return ToolResult("read_file", False, None, error=f"File not found: {file_path}")

        # Guard against reading huge binary files
        if target.stat().st_size > 5 * 1024 * 1024:
            return ToolResult("read_file", False, None, error="File exceeds 5MB safety limit.")

        with open(target, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        s_idx = max(0, start_line - 1)
        e_idx = min(total_lines, end_line)
        slice_content = "".join(lines[s_idx:e_idx])

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="read_file",
            success=True,
            data={
                "file_path": file_path,
                "start_line": start_line,
                "end_line": e_idx,
                "total_lines": total_lines,
                "content": redact_credentials(slice_content),
            },
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("read_file", False, None, error=str(exc))


def tool_search_code(workspace_path: str, pattern: str, file_pattern: str = "*", max_results: int = 30) -> ToolResult:
    """Search for regex patterns across files."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        regex = re.compile(pattern, re.IGNORECASE)
        results = []

        for path in base.rglob(file_pattern):
            if path.is_dir() or any(p.startswith(".") or p in ("node_modules", "venv", ".venv") for p in path.parts):
                continue
            if path.stat().st_size > 1024 * 1024:
                continue

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append({
                                "file": str(path.relative_to(base)),
                                "line_number": line_no,
                                "match": line.strip()[:200],
                            })
                            if len(results) >= max_results:
                                break
            except Exception:
                continue

            if len(results) >= max_results:
                break

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="search_code",
            success=True,
            data={"pattern": pattern, "matches": results, "count": len(results)},
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("search_code", False, None, error=str(exc))


def tool_inspect_dependencies(workspace_path: str) -> ToolResult:
    """Inspect package manifests (package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod)."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        manifests = {}

        # 1. Node.js (package.json)
        pkg_json = base / "package.json"
        if pkg_json.exists():
            try:
                with open(pkg_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    manifests["npm"] = {
                        "name": data.get("name"),
                        "dependencies": data.get("dependencies", {}),
                        "devDependencies": data.get("devDependencies", {}),
                        "scripts": data.get("scripts", {}),
                    }
            except Exception as e:
                manifests["npm"] = {"error": str(e)}

        # 2. Python (requirements.txt)
        req_txt = base / "requirements.txt"
        if req_txt.exists():
            with open(req_txt, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
                manifests["pip"] = {"packages": lines}

        # 3. Python (pyproject.toml)
        pyproject = base / "pyproject.toml"
        if pyproject.exists():
            manifests["pyproject"] = {"found": True, "path": "pyproject.toml"}

        # 4. Rust (Cargo.toml)
        cargo = base / "Cargo.toml"
        if cargo.exists():
            manifests["cargo"] = {"found": True, "path": "Cargo.toml"}

        # 5. Go (go.mod)
        gomod = base / "go.mod"
        if gomod.exists():
            manifests["go"] = {"found": True, "path": "go.mod"}

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="inspect_dependencies",
            success=True,
            data={"manifests": manifests},
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("inspect_dependencies", False, None, error=str(exc))


def tool_inspect_configuration(workspace_path: str) -> ToolResult:
    """Detect environment configs, dockerfiles, CI workflows, and linters."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        configs = {
            "env_files": [],
            "docker_files": [],
            "ci_workflows": [],
            "build_tools": [],
        }

        for path in base.rglob("*"):
            if any(p in ("node_modules", ".venv", ".git") for p in path.parts):
                continue
            rel = str(path.relative_to(base))
            if path.name.startswith(".env"):
                configs["env_files"].append(rel)
            elif "dockerfile" in path.name.lower() or path.name.endswith(".dockerfile"):
                configs["docker_files"].append(rel)
            elif ".github/workflows" in rel:
                configs["ci_workflows"].append(rel)
            elif path.name in ("Makefile", "tsconfig.json", "vite.config.js", "vite.config.ts", "webpack.config.js"):
                configs["build_tools"].append(rel)

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="inspect_configuration",
            success=True,
            data=configs,
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("inspect_configuration", False, None, error=str(exc))


def tool_inspect_git_history(workspace_path: str, max_commits: int = 10) -> ToolResult:
    """Inspect recent git commit messages and hashes."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        git_dir = base / ".git"
        if not git_dir.exists():
            return ToolResult(
                tool_name="inspect_git_history",
                success=True,
                data={"commits": [], "message": "Not a git repository."},
                execution_time_ms=0.0,
            )

        cmd = ["git", "log", f"-n{max_commits}", "--pretty=format:%h|%an|%ar|%s"]
        res = subprocess.run(cmd, cwd=str(base), capture_output=True, text=True, timeout=10)
        commits = []
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                    })

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="inspect_git_history",
            success=True,
            data={"commits": commits},
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("inspect_git_history", False, None, error=str(exc))


def register_repository_tools(registry: Any) -> None:
    """Register all 6 repository tools."""
    registry.register(ToolDefinition(
        name="list_files",
        category="repository",
        description="List files in a workspace directory within a safe depth.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to the workspace root"),
            ToolParameter("subpath", "string", "Relative subfolder", required=False, default="."),
            ToolParameter("max_depth", "integer", "Maximum directory depth", required=False, default=3),
        ],
        handler=tool_list_files,
    ))

    registry.register(ToolDefinition(
        name="read_file",
        category="repository",
        description="Read lines from a safe workspace file with credential redaction.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to the workspace root"),
            ToolParameter("file_path", "string", "Relative file path to read"),
            ToolParameter("start_line", "integer", "Starting line (1-indexed)", required=False, default=1),
            ToolParameter("end_line", "integer", "Ending line (inclusive)", required=False, default=500),
        ],
        handler=tool_read_file,
    ))

    registry.register(ToolDefinition(
        name="search_code",
        category="repository",
        description="Search for regex patterns across files in the workspace.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("pattern", "string", "Regex pattern to match"),
            ToolParameter("file_pattern", "string", "File glob filter (e.g. *.py, *.ts)", required=False, default="*"),
            ToolParameter("max_results", "integer", "Max matches to return", required=False, default=30),
        ],
        handler=tool_search_code,
    ))

    registry.register(ToolDefinition(
        name="inspect_dependencies",
        category="repository",
        description="Inspect manifest files (package.json, requirements.txt, pyproject.toml, etc.).",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
        ],
        handler=tool_inspect_dependencies,
    ))

    registry.register(ToolDefinition(
        name="inspect_configuration",
        category="repository",
        description="Inspect environment files, Dockerfiles, and CI workflow configurations.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
        ],
        handler=tool_inspect_configuration,
    ))

    registry.register(ToolDefinition(
        name="inspect_git_history",
        category="repository",
        description="Inspect recent git commit messages and hashes.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("max_commits", "integer", "Max commits to inspect", required=False, default=10),
        ],
        handler=tool_inspect_git_history,
    ))
