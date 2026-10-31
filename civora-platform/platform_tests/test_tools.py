"""Unit tests for CIVORA Intelligent Tools."""

import pytest
from pathlib import Path
from tools import create_default_registry


@pytest.fixture
def registry():
    return create_default_registry()


def test_registry_registration(registry):
    tools = registry.list_all()
    assert len(tools) >= 16
    names = [t.name for t in tools]
    assert "list_files" in names
    assert "read_file" in names
    assert "search_code" in names
    assert "inspect_dependencies" in names
    assert "execute_command" in names
    assert "generate_patch" in names
    assert "apply_patch" in names
    assert "rollback_patch" in names
    assert "clean_room_verification" in names
    assert "generate_report" in names


def test_list_and_read_files(registry, tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "file1.txt").write_text("line1\nline2\nline3\n")

    res_list = registry.execute("list_files", workspace_path=str(ws))
    assert res_list.success
    assert "file1.txt" in res_list.data["files"]

    res_read = registry.execute("read_file", workspace_path=str(ws), file_path="file1.txt", start_line=1, end_line=2)
    assert res_read.success
    assert "line1" in res_read.data["content"]


def test_patch_apply_and_rollback(registry, tmp_path):
    ws = tmp_path / "repo"
    ws.mkdir()
    target_file = ws / "config.json"
    target_file.write_text('{"version": "1.0.0"}\n')

    # Apply patch
    res_apply = registry.execute(
        "apply_patch",
        workspace_path=str(ws),
        file_path="config.json",
        modified_content='{"version": "2.0.0"}\n',
        explanation="Version bump to 2.0.0",
    )
    assert res_apply.success
    assert target_file.read_text() == '{"version": "2.0.0"}\n'
    patch_id = res_apply.data["patch_id"]

    # Rollback patch
    res_rollback = registry.execute("rollback_patch", workspace_path=str(ws), patch_id=patch_id)
    assert res_rollback.success
    assert target_file.read_text() == '{"version": "1.0.0"}\n'


def test_inspect_logs_extracts_stack_trace(registry):
    sample_trace = (
        "Starting test run...\n"
        "Traceback (most recent call last):\n"
        "  File 'main.py', line 12, in <module>\n"
        "ModuleNotFoundError: No module named 'fastapi'\n"
    )
    res = registry.execute("inspect_logs", raw_log=sample_trace)
    assert res.success
    assert res.data["error_count"] >= 1
    assert len(res.data["stack_traces"]) >= 1
