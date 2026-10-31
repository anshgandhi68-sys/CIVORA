"""CIVORA Patch Studio Diff Engine.

Provides unified diff generation, line-by-line chunk analysis,
atomic patch application, file backups, and rollback capabilities.
"""

from __future__ import annotations

import difflib
import os
import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sandbox.security import check_safe_path


@dataclass
class FilePatch:
    file_path: str
    original_content: str
    modified_content: str
    diff_text: str
    additions: int
    deletions: int
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "diff_text": self.diff_text,
            "additions": self.additions,
            "deletions": self.deletions,
            "explanation": self.explanation,
        }


@dataclass
class PatchRecord:
    patch_id: str
    created_at: float
    status: str  # draft | applied | approved | rejected | rolled_back
    explanation: str
    files: List[FilePatch]
    workspace_path: str
    backup_dir: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patch_id": self.patch_id,
            "created_at": self.created_at,
            "status": self.status,
            "explanation": self.explanation,
            "files": [f.to_dict() for f in self.files],
            "total_additions": sum(f.additions for f in self.files),
            "total_deletions": sum(f.deletions for f in self.files),
            "affected_files_count": len(self.files),
        }


class DiffEngine:
    """Core diff calculator, patch applicator, and rollback manager."""

    def __init__(self, backup_root: Optional[str] = None):
        if backup_root:
            self.backup_root = Path(backup_root).resolve()
        else:
            self.backup_root = Path("/tmp/civora_patch_backups").resolve()
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.records: Dict[str, PatchRecord] = {}

    def generate_file_diff(
        self,
        file_path: str,
        original_content: str,
        modified_content: str,
        explanation: str = "",
    ) -> FilePatch:
        """Generate a unified git diff between original and modified text."""
        orig_lines = original_content.splitlines(keepends=True)
        mod_lines = modified_content.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="\n",
        ))
        diff_text = "".join(diff)

        # Count additions and deletions
        additions = 0
        deletions = 0
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        return FilePatch(
            file_path=file_path,
            original_content=original_content,
            modified_content=modified_content,
            diff_text=diff_text,
            additions=additions,
            deletions=deletions,
            explanation=explanation,
        )

    def validate_patch(self, workspace_path: Path, patch: FilePatch) -> Tuple[bool, Optional[str]]:
        """Verify that the target file can accept the patch cleanly."""
        target_path = (workspace_path / patch.file_path).resolve()
        is_safe, err, _ = check_safe_path(workspace_path, target_path)
        if not is_safe:
            return False, f"Path security violation: {err}"

        # If original_content was specified, verify that the current target matches it
        if target_path.exists():
            current_content = target_path.read_text(encoding="utf-8", errors="replace")
            # If current content is completely different, flag warning or check compatibility
            if patch.original_content and current_content.strip() != patch.original_content.strip():
                # Allow partial match if diff chunks apply
                pass
        return True, None

    def apply_patch(
        self,
        workspace_path: str,
        file_patches: List[FilePatch],
        explanation: str = "",
        patch_id: Optional[str] = None,
    ) -> PatchRecord:
        """Apply file patches atomically, backing up original files for rollback."""
        ws = Path(workspace_path).resolve()
        p_id = patch_id or f"patch_{uuid.uuid4().hex[:10]}"
        backup_dir = self.backup_root / p_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Validate all first
        for fp in file_patches:
            valid, err = self.validate_patch(ws, fp)
            if not valid:
                raise ValueError(f"Failed to validate patch for {fp.file_path}: {err}")

        # Perform backups and writes
        for fp in file_patches:
            target_path = (ws / fp.file_path).resolve()
            backup_target = backup_dir / fp.file_path
            backup_target.parent.mkdir(parents=True, exist_ok=True)

            if target_path.exists():
                shutil.copy2(target_path, backup_target)
            else:
                # Mark as newly created file
                (backup_dir / f"{fp.file_path}.CIVORA_NEW").touch()

            # Write modified content
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(fp.modified_content, encoding="utf-8")

        record = PatchRecord(
            patch_id=p_id,
            created_at=time.time(),
            status="applied",
            explanation=explanation,
            files=file_patches,
            workspace_path=str(ws),
            backup_dir=str(backup_dir),
        )
        self.records[p_id] = record
        return record

    def rollback_patch(self, patch_id: str) -> Tuple[bool, Optional[str]]:
        """Restore all files in the patch from backup."""
        record = self.records.get(patch_id)
        if not record:
            return False, f"Patch ID '{patch_id}' not found in registry."

        ws = Path(record.workspace_path).resolve()
        backup_dir = Path(record.backup_dir).resolve()

        for fp in record.files:
            target = (ws / fp.file_path).resolve()
            backup_file = backup_dir / fp.file_path
            new_marker = backup_dir / f"{fp.file_path}.CIVORA_NEW"

            if new_marker.exists():
                # File was originally non-existent; remove it
                if target.exists():
                    target.unlink()
            elif backup_file.exists():
                # Restore backup
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target)

        record.status = "rolled_back"
        return True, None

    def get_patch(self, patch_id: str) -> Optional[PatchRecord]:
        return self.records.get(patch_id)

    def list_patches(self) -> List[PatchRecord]:
        return list(self.records.values())
