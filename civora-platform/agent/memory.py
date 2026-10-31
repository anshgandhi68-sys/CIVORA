"""CIVORA Agent Memory and Persistent Task Storage.

Maintains SQLite tables for tasks, execution plans, tool audit traces,
detected findings, candidate patches, and counterfactual verifications.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class StepRecord:
    task_id: str
    step_number: int
    phase: str
    action: str
    status: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "step_number": self.step_number,
            "phase": self.phase,
            "action": self.action,
            "status": self.status,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "tool_result": self.tool_result,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": round(self.duration_ms, 2),
        }


@dataclass
class TaskRecord:
    task_id: str
    title: str
    prompt: str
    status: str  # PENDING | RUNNING | VERIFIED | FAILED | ABORTED
    created_at: float
    finished_at: Optional[float] = None
    report_md: Optional[str] = None
    steps: List[StepRecord] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "prompt": self.prompt,
            "status": self.status,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "report_md": self.report_md,
            "steps": [s.to_dict() for s in self.steps],
            "findings": self.findings,
        }


class AgentMemory:
    """Persistent storage backed by SQLite for continuous agent execution traces."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path).resolve()
        else:
            self.db_path = Path(__file__).parent.parent / "civora_agent.db"
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT,
                prompt TEXT,
                status TEXT,
                created_at REAL,
                finished_at REAL,
                report_md TEXT
            );

            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                step_number INTEGER,
                phase TEXT,
                action TEXT,
                status TEXT,
                tool_name TEXT,
                tool_args TEXT,
                tool_result TEXT,
                stdout TEXT,
                stderr TEXT,
                duration_ms REAL,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            );

            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                finding_id TEXT,
                category TEXT,
                severity TEXT,
                title TEXT,
                explanation TEXT,
                evidence TEXT,
                suggested_fix TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            );

            CREATE TABLE IF NOT EXISTS patches (
                patch_id TEXT PRIMARY KEY,
                task_id TEXT,
                status TEXT,
                diff_text TEXT,
                additions INTEGER,
                deletions INTEGER,
                explanation TEXT,
                created_at REAL,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            );
            """)

    def create_task(self, task_id: str, title: str, prompt: str) -> TaskRecord:
        now = time.time()
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO tasks (task_id, title, prompt, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (task_id, title, prompt, "RUNNING", now),
            )
        return TaskRecord(task_id=task_id, title=title, prompt=prompt, status="RUNNING", created_at=now)

    def update_task_status(self, task_id: str, status: str, report_md: Optional[str] = None) -> None:
        now = time.time()
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE tasks SET status = ?, finished_at = ?, report_md = coalesce(?, report_md) WHERE task_id = ?",
                (status, now, report_md, task_id),
            )

    def record_step(self, step: StepRecord) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO steps (task_id, step_number, phase, action, status, tool_name, tool_args, tool_result, stdout, stderr, duration_ms)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    step.task_id,
                    step.step_number,
                    step.phase,
                    step.action,
                    step.status,
                    step.tool_name,
                    json.dumps(step.tool_args) if step.tool_args else None,
                    json.dumps(step.tool_result) if step.tool_result else None,
                    step.stdout,
                    step.stderr,
                    step.duration_ms,
                ),
            )

    def record_finding(self, task_id: str, finding: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO findings (task_id, finding_id, category, severity, title, explanation, evidence, suggested_fix)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task_id,
                    finding.get("id"),
                    finding.get("category"),
                    finding.get("severity"),
                    finding.get("title"),
                    finding.get("explanation"),
                    finding.get("evidence"),
                    finding.get("suggested_fix"),
                ),
            )

    def record_patch(self, task_id: str, patch_data: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO patches (patch_id, task_id, status, diff_text, additions, deletions, explanation, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    patch_data.get("patch_id"),
                    task_id,
                    patch_data.get("status", "applied"),
                    patch_data.get("diff_text", ""),
                    patch_data.get("additions", 0),
                    patch_data.get("deletions", 0),
                    patch_data.get("explanation", ""),
                    time.time(),
                ),
            )

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            t_row = cur.fetchone()
            if not t_row:
                return None

            # Get steps
            s_cur = conn.execute("SELECT * FROM steps WHERE task_id = ? ORDER BY step_number ASC", (task_id,))
            steps = []
            for s in s_cur.fetchall():
                steps.append(StepRecord(
                    task_id=s["task_id"],
                    step_number=s["step_number"],
                    phase=s["phase"],
                    action=s["action"],
                    status=s["status"],
                    tool_name=s["tool_name"],
                    tool_args=json.loads(s["tool_args"]) if s["tool_args"] else None,
                    tool_result=json.loads(s["tool_result"]) if s["tool_result"] else None,
                    stdout=s["stdout"],
                    stderr=s["stderr"],
                    duration_ms=s["duration_ms"],
                ))

            # Get findings
            f_cur = conn.execute("SELECT * FROM findings WHERE task_id = ?", (task_id,))
            findings = [dict(f) for f in f_cur.fetchall()]

            return TaskRecord(
                task_id=t_row["task_id"],
                title=t_row["title"],
                prompt=t_row["prompt"],
                status=t_row["status"],
                created_at=t_row["created_at"],
                finished_at=t_row["finished_at"],
                report_md=t_row["report_md"],
                steps=steps,
                findings=findings,
            )

    def list_recent_tasks(self, limit: int = 15) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT task_id, title, prompt, status, created_at, finished_at FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]

