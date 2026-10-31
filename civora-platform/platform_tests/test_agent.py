"""Unit tests for Agent Orchestrator and Memory."""

import pytest
import asyncio
from pathlib import Path
from agent import AgentMemory, StepRecord, AgentOrchestrator


def test_agent_memory(tmp_path):
    db_file = tmp_path / "test_memory.db"
    mem = AgentMemory(str(db_file))

    task = mem.create_task("t_123", "Test Title", "Prompt instruction")
    assert task.status == "RUNNING"

    step = StepRecord(
        task_id="t_123",
        step_number=1,
        phase="OBSERVE",
        action="Scanning files",
        status="COMPLETED",
        stdout="Found 5 files",
    )
    mem.record_step(step)

    retrieved = mem.get_task("t_123")
    assert retrieved is not None
    assert len(retrieved.steps) == 1
    assert retrieved.steps[0].action == "Scanning files"


@pytest.mark.asyncio
async def test_agent_orchestrator_loop(tmp_path):
    repo = tmp_path / "mock_repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Mock\n```bash\nnpm install\n```\n")
    (repo / "package.json").write_text('{"name": "mock", "scripts": {"test": "echo success"}}\n')

    db_file = tmp_path / "orch_test.db"
    orch = AgentOrchestrator(memory=AgentMemory(str(db_file)))

    task = await orch.run_autonomous_loop(
        task_id="orch_task_1",
        prompt="Perform automated drift detection and verification",
        repo_path=str(repo),
    )

    assert task.status in ("VERIFIED", "COMPLETED")
    assert len(task.steps) >= 5
