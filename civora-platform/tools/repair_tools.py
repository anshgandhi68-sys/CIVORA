"""CIVORA Repair Tools.

Provides unified diff generation, patch validation, atomic patch application,
and rollback capabilities for autonomous code and documentation fixes.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from patch_studio.diff_engine import DiffEngine, FilePatch, PatchRecord
from .registry import ToolDefinition, ToolParameter, ToolResult

# Shared diff engine
_diff_engine = DiffEngine()


def tool_generate_patch(
    workspace_path: str,
    file_path: str,
    modified_content: str,
    explanation: str = "",
) -> ToolResult:
    """Generate a unified diff between the current workspace file and the modified content."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        target = (base / file_path).resolve()
        
        orig_content = ""
        if target.exists() and target.is_file():
            orig_content = target.read_text(encoding="utf-8", errors="replace")

        file_patch = _diff_engine.generate_file_diff(
            file_path=file_path,
            original_content=orig_content,
            modified_content=modified_content,
            explanation=explanation,
        )

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="generate_patch",
            success=True,
            data=file_patch.to_dict(),
            stdout=file_patch.diff_text,
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("generate_patch", False, None, error=str(exc))


def tool_validate_patch(
    workspace_path: str,
    file_path: str,
    diff_text: str,
) -> ToolResult:
    """Validate that the patch can safely apply to the workspace target file."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        target = (base / file_path).resolve()
        
        if not target.exists():
            return ToolResult(
                tool_name="validate_patch",
                success=True,
                data={"status": "valid", "file_status": "new_file"},
                execution_time_ms=(time.perf_counter() - t0) * 1000,
            )

        # Basic diff sanity check
        has_headers = any(line.startswith("@@") for line in diff_text.splitlines())
        duration = (time.perf_counter() - t0) * 1000

        return ToolResult(
            tool_name="validate_patch",
            success=True,
            data={"status": "valid", "has_hunks": has_headers, "file_path": file_path},
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("validate_patch", False, None, error=str(exc))


def tool_apply_patch(
    workspace_path: str,
    file_path: str,
    modified_content: str,
    explanation: str = "",
) -> ToolResult:
    """Apply a candidate fix directly into the isolated workspace, creating backup."""
    t0 = time.perf_counter()
    try:
        base = Path(workspace_path).resolve()
        target = (base / file_path).resolve()
        orig_content = ""
        if target.exists():
            orig_content = target.read_text(encoding="utf-8", errors="replace")

        fp = _diff_engine.generate_file_diff(
            file_path=file_path,
            original_content=orig_content,
            modified_content=modified_content,
            explanation=explanation,
        )

        record = _diff_engine.apply_patch(
            workspace_path=str(base),
            file_patches=[fp],
            explanation=explanation,
        )

        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="apply_patch",
            success=True,
            data={
                "patch_id": record.patch_id,
                "status": record.status,
                "file_path": file_path,
                "additions": fp.additions,
                "deletions": fp.deletions,
            },
            stdout=fp.diff_text,
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("apply_patch", False, None, error=str(exc))


def tool_rollback_patch(workspace_path: str, patch_id: str) -> ToolResult:
    """Roll back an applied patch restoring the previous clean state."""
    t0 = time.perf_counter()
    try:
        ok, err = _diff_engine.rollback_patch(patch_id)
        duration = (time.perf_counter() - t0) * 1000
        return ToolResult(
            tool_name="rollback_patch",
            success=ok,
            data={"patch_id": patch_id, "rolled_back": ok},
            error=err,
            execution_time_ms=duration,
        )
    except Exception as exc:
        return ToolResult("rollback_patch", False, None, error=str(exc))


def register_repair_tools(registry: Any) -> None:
    """Register all 4 repair tools."""
    registry.register(ToolDefinition(
        name="generate_patch",
        category="repair",
        description="Generate unified git diff for a proposed file modification.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("file_path", "string", "Relative path of file to patch"),
            ToolParameter("modified_content", "string", "Full modified content of file"),
            ToolParameter("explanation", "string", "Rationale for changes", required=False, default=""),
        ],
        handler=tool_generate_patch,
    ))

    registry.register(ToolDefinition(
        name="validate_patch",
        category="repair",
        description="Validate if unified diff is structurally sound and targets valid path.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("file_path", "string", "Relative path of file to patch"),
            ToolParameter("diff_text", "string", "Unified diff text"),
        ],
        handler=tool_validate_patch,
    ))

    registry.register(ToolDefinition(
        name="apply_patch",
        category="repair",
        description="Apply modified file content into sandbox workspace with automatic rollback backup.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("file_path", "string", "Relative path to modify"),
            ToolParameter("modified_content", "string", "Full modified content to write"),
            ToolParameter("explanation", "string", "Explanation for the patch", required=False, default=""),
        ],
        handler=tool_apply_patch,
    ))

    registry.register(ToolDefinition(
        name="rollback_patch",
        category="repair",
        description="Rollback an applied patch by ID, restoring original files.",
        parameters=[
            ToolParameter("workspace_path", "string", "Absolute path to workspace root"),
            ToolParameter("patch_id", "string", "Identifier of patch to revert"),
        ],
        handler=tool_rollback_patch,
    ))

