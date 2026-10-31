"""Test Suite for CIVORA Developer Platform and Universal OpenAI-Compatible API.

Verifies:
- Universal API Key generation, SHA-256 hashing, masking, and zero plaintext leaks
- Bearer authentication and security boundary enforcement
- OpenAI-compatible /v1/models, /v1/chat/completions, /v1/usage, /v1/embeddings
- Server-Sent Events (SSE) streaming compatibility
- Per-key sliding-window rate limiting (RPM) and HTTP 429 enforcement
- Developer telemetry, token usage tracking, and key lifecycle (revoke, regenerate, delete)
"""

import json
import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
PLATFORM_ROOT = Path(__file__).parent.parent.resolve()
if str(PLATFORM_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_ROOT))

import main
from developer.auth import hash_api_key, create_developer_api_key, dev_db
from developer.rate_limiter import SlidingWindowRateLimiter


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture
def test_key():
    account = dev_db.get_default_account()
    record, raw_key = create_developer_api_key(
        developer_id=account.id,
        name="Automated Test Key",
        environment="test",
        rate_limit_rpm=30,
        quota_monthly=50000,
    )
    return {"record": record, "raw_key": raw_key, "account": account}


def test_api_key_security_and_hashing(test_key):
    """Verify keys are cryptographically secure, formatted correctly, and hashed in DB."""
    raw_key = test_key["raw_key"]
    record = test_key["record"]

    # Verify key prefix and structure
    assert raw_key.startswith("civora_sk_test_")
    assert len(raw_key) > 40

    # Verify that raw_key is NEVER stored in database
    db_record = dev_db.get_api_key_by_id(record.id)
    assert db_record is not None
    assert db_record.key_hash == hash_api_key(raw_key)
    assert raw_key not in db_record.key_hash
    assert db_record.key_prefix.startswith("civora_sk_test_")
    assert "••••••" in db_record.key_prefix


def test_models_endpoint(client):
    """Verify /v1/models lists all 4 CIVORA logical models."""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    
    model_ids = [m["id"] for m in data["data"]]
    assert "civora-general" in model_ids
    assert "civora-coder" in model_ids
    assert "civora-repository-agent" in model_ids
    assert "civora-engineering-agent" in model_ids

    # Single model retrieve
    m_resp = client.get("/v1/models/civora-coder")
    assert m_resp.status_code == 200
    assert m_resp.json()["id"] == "civora-coder"


def test_missing_or_invalid_auth(client):
    """Verify proper 401 rejection for missing, malformed, or invalid keys."""
    # 1. Missing header
    res1 = client.post("/v1/chat/completions", json={"model": "civora-coder", "messages": [{"role": "user", "content": "hi"}]})
    assert res1.status_code == 401
    assert res1.json()["detail"]["error"]["code"] == "missing_api_key"

    # 2. Malformed key format
    res2 = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer sk-invalid-key-format"},
        json={"model": "civora-coder", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert res2.status_code == 401
    assert res2.json()["detail"]["error"]["code"] == "invalid_api_key_format"

    # 3. Non-existent key with proper prefix
    res3 = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer civora_sk_live_00000000000000000000000000000000"},
        json={"model": "civora-coder", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert res3.status_code == 401
    assert res3.json()["detail"]["error"]["code"] == "invalid_api_key"


def test_revoked_key_rejection(client, test_key):
    """Verify revoked key is immediately blocked."""
    raw_key = test_key["raw_key"]
    record = test_key["record"]

    # Revoke key
    dev_db.revoke_api_key(record.id)

    res = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={"model": "civora-coder", "messages": [{"role": "user", "content": "hello"}]},
    )
    assert res.status_code == 401
    assert res.json()["detail"]["error"]["code"] == "api_key_revoked"


def test_chat_completions_sync(client, test_key):
    """Verify OpenAI-compatible non-streaming chat completions."""
    raw_key = test_key["raw_key"]
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={
            "model": "civora-coder",
            "messages": [
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Write a python function to add two numbers."},
            ],
            "temperature": 0.5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["model"] == "civora-coder"
    assert len(data["choices"]) > 0
    assert "choices" in data
    assert "usage" in data
    assert data["usage"]["total_tokens"] > 0
    assert "x-ratelimit-remaining-requests" in response.headers


def test_chat_completions_streaming(client, test_key):
    """Verify OpenAI-compatible Server-Sent Events (SSE) streaming."""
    raw_key = test_key["raw_key"]
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={
            "model": "civora-general",
            "messages": [{"role": "user", "content": "Explain microservices architecture."}],
            "stream": True,
        },
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    lines = response.text.split("\n")
    data_lines = [line for line in lines if line.startswith("data: ")]
    assert len(data_lines) >= 2
    assert "data: [DONE]" in data_lines

    # Check first chunk structure
    first_payload = json.loads(data_lines[0].replace("data: ", ""))
    assert first_payload["object"] == "chat.completion.chunk"
    assert first_payload["model"] == "civora-general"


def test_rate_limiting_enforcement(client):
    """Verify sliding-window rate limit enforces 429 Too Many Requests."""
    account = dev_db.get_default_account()
    record, raw_key = create_developer_api_key(
        developer_id=account.id,
        name="Strict Rate Key",
        environment="test",
        rate_limit_rpm=2,  # Only 2 requests allowed per minute
    )

    # First request: 200
    r1 = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={"model": "civora-general", "messages": [{"role": "user", "content": "1"}]},
    )
    assert r1.status_code == 200

    # Second request: 200
    r2 = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={"model": "civora-general", "messages": [{"role": "user", "content": "2"}]},
    )
    assert r2.status_code == 200

    # Third request: 429 Rate Limit Exceeded
    r3 = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={"model": "civora-general", "messages": [{"role": "user", "content": "3"}]},
    )
    assert r3.status_code == 429
    assert r3.json()["detail"]["error"]["code"] == "rate_limit_exceeded"


def test_key_usage_and_analytics(client, test_key):
    """Verify /v1/usage and /api/developer/analytics endpoints."""
    raw_key = test_key["raw_key"]

    # Call /v1/usage
    res = client.get("/v1/usage", headers={"Authorization": f"Bearer {raw_key}"})
    assert res.status_code == 200
    data = res.json()
    assert data["object"] == "usage"
    assert "monthly_quota_tokens" in data
    assert "account_analytics" in data

    # Call /api/developer/analytics
    analytics_res = client.get("/api/developer/analytics")
    assert analytics_res.status_code == 200
    a_data = analytics_res.json()
    assert "total_requests" in a_data
    assert "models_breakdown" in a_data


def test_developer_key_lifecycle(client):
    """Verify Key creation, listing, rotation (regeneration), and deletion via dashboard API."""
    # 1. Create key
    create_res = client.post(
        "/api/developer/keys",
        json={"name": "Lifecycle Test Key", "environment": "live", "rate_limit_rpm": 60, "quota_monthly": 100000},
    )
    assert create_res.status_code == 200
    key_data = create_res.json()
    key_id = key_data["id"]
    secret_key = key_data["secret_key"]
    assert secret_key.startswith("civora_sk_live_")

    # 2. List keys
    list_res = client.get("/api/developer/keys")
    assert list_res.status_code == 200
    keys = list_res.json()
    found = [k for k in keys if k["id"] == key_id]
    assert len(found) == 1
    assert "••••••" in found[0]["key_prefix"]
    assert "secret_key" not in found[0]  # Secret must NOT be exposed in list

    # 3. Regenerate (rotate)
    regen_res = client.post(f"/api/developer/keys/{key_id}/regenerate")
    assert regen_res.status_code == 200
    new_key_data = regen_res.json()["new_key"]
    assert new_key_data["secret_key"].startswith("civora_sk_live_")
    new_key_id = new_key_data["id"]

    # Verify old key revoked
    revoked_key = dev_db.get_api_key_by_id(key_id)
    assert revoked_key.is_active is False

    # 4. Delete new key
    del_res = client.delete(f"/api/developer/keys/{new_key_id}")
    assert del_res.status_code == 200
    assert dev_db.get_api_key_by_id(new_key_id) is None


def test_embeddings_endpoint(client, test_key):
    """Verify /v1/embeddings returns standard vector embeddings."""
    raw_key = test_key["raw_key"]
    res = client.post(
        "/v1/embeddings",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={"model": "civora-embeddings", "input": ["def test_code(): pass", "SELECT * FROM users"]},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["object"] == "list"
    assert len(data["data"]) == 2
    assert len(data["data"][0]["embedding"]) == 1536
