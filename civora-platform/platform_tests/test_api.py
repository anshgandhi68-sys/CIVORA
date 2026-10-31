"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add civora-platform to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


def test_repo_scan_api():
    response = client.post("/api/repo/scan", json={"repo_path": str(Path(__file__).parent.parent)})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "languages" in data
    assert "driftIssues" in data


def test_sandbox_exec_api_allowed():
    response = client.post("/api/sandbox/exec", json={"command": "echo 'civora test'"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "civora test" in data["stdout"]


def test_sandbox_exec_api_blocked():
    response = client.post("/api/sandbox/exec", json={"command": "rm -rf /some/dir"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert "Zero-Trust" in data["stderr"] or not data["allowed"]


def test_patch_generate_api():
    response = client.post("/api/patch/generate", json={
        "file_path": "README.md",
        "original_content": "old text",
        "modified_content": "new text",
        "explanation": "Update text",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["additions"] == 1
    assert data["deletions"] == 1
    assert "diff_text" in data


def test_ai_chat_api():
    response = client.post("/api/ai/chat", json={
        "messages": [{"role": "user", "content": "How do you detect documentation drift?"}],
        "mode": "agent",
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
