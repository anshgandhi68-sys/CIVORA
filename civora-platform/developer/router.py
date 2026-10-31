"""CIVORA Developer Platform Router.

Mounts:
- OpenAI-compatible endpoints: /v1/chat/completions, /v1/models, /v1/usage, /v1/embeddings
- Developer dashboard management endpoints: /api/developer/keys, /api/developer/analytics, etc.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from .auth import (
    create_developer_api_key,
    dev_db,
    hash_api_key,
    mask_api_key,
    verify_api_key,
)
from .database import ApiKeyRecord, DeveloperAccount
from .models import (
    ApiKeyCreatedResponse,
    ApiKeySummary,
    ChatCompletionRequest,
    ChatCompletionResponse,
    CreateApiKeyRequest,
    DeveloperAnalyticsResponse,
    EmbeddingData,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelListResponse,
    UsageMetrics,
)
from .rate_limiter import rate_limiter
from .service import CIVORA_MODELS, estimate_tokens, get_available_models, model_service

router = APIRouter(tags=["Developer Platform & Universal API"])


# -----------------------------------------------------------------------------
# 1. OPENAI-COMPATIBLE V1 ENDPOINTS
# -----------------------------------------------------------------------------

@router.get("/v1/models", response_model=ModelListResponse)
async def list_models():
    """List all available CIVORA models in OpenAI-compatible format."""
    return ModelListResponse(data=get_available_models())


@router.get("/v1/models/{model_id}")
async def retrieve_model(model_id: str):
    """Retrieve details for a specific CIVORA model."""
    if model_id not in CIVORA_MODELS:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "message": f"The model '{model_id}' does not exist.",
                    "type": "invalid_request_error",
                    "param": "model",
                    "code": "model_not_found",
                }
            },
        )
    info = CIVORA_MODELS[model_id]
    return {
        "id": model_id,
        "object": "model",
        "created": 1730300000,
        "owned_by": "civora-ai",
        "description": info["description"],
    }


@router.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    body: ChatCompletionRequest,
    auth_data: Tuple[ApiKeyRecord, DeveloperAccount] = Depends(verify_api_key),
):
    """Universal OpenAI-compatible chat completions endpoint.
    
    Supports:
    - Models: civora-general, civora-coder, civora-repository-agent, civora-engineering-agent
    - Streaming: SSE via `stream=true`
    - Per-key rate limiting (RPM) and usage tracking
    """
    key_record, account = auth_data
    start_time = time.time()

    # Enforce sliding-window rate limit
    ratelimit_headers = rate_limiter.enforce(key_record.id, key_record.rate_limit_rpm)

    client_ip = request.client.host if request.client else "127.0.0.1"

    # Streaming mode
    if body.stream:
        # Record approximate usage telemetry for streaming initiation
        prompt_tokens = estimate_tokens(" ".join([m.content for m in body.messages]))
        dev_db.record_request(
            key_id=key_record.id,
            developer_id=account.id,
            model=body.model,
            endpoint="/v1/chat/completions",
            prompt_tokens=prompt_tokens,
            completion_tokens=60,  # Estimated baseline for streaming
            latency_ms=15.0,
            status_code=200,
            ip_address=client_ip,
        )

        stream_gen = model_service.stream_completion(body)
        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            **ratelimit_headers,
        }
        return StreamingResponse(stream_gen, media_type="text/event-stream", headers=headers)

    # Non-streaming mode
    try:
        response_obj, latency_ms = await model_service.complete(body)
        
        # Record request telemetry in SQLite
        dev_db.record_request(
            key_id=key_record.id,
            developer_id=account.id,
            model=body.model,
            endpoint="/v1/chat/completions",
            prompt_tokens=response_obj.usage.prompt_tokens,
            completion_tokens=response_obj.usage.completion_tokens,
            latency_ms=latency_ms,
            status_code=200,
            ip_address=client_ip,
        )

        return JSONResponse(content=response_obj.model_dump(), headers=ratelimit_headers)
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        dev_db.record_request(
            key_id=key_record.id,
            developer_id=account.id,
            model=body.model,
            endpoint="/v1/chat/completions",
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=latency_ms,
            status_code=500,
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"CIVORA model processing error: {str(e)}",
                    "type": "api_error",
                    "param": None,
                    "code": "internal_error",
                }
            },
        )


@router.get("/v1/usage")
async def get_key_usage(
    auth_data: Tuple[ApiKeyRecord, DeveloperAccount] = Depends(verify_api_key),
):
    """Retrieve usage metrics and quota consumption for authenticated key."""
    key_record, account = auth_data
    monthly_used = dev_db.get_monthly_token_usage(key_record.id)
    analytics = dev_db.get_developer_analytics(account.id)

    return {
        "object": "usage",
        "key_id": key_record.id,
        "key_name": key_record.name,
        "environment": key_record.environment,
        "monthly_quota_tokens": key_record.quota_monthly,
        "monthly_used_tokens": monthly_used,
        "remaining_tokens": max(0, key_record.quota_monthly - monthly_used),
        "rate_limit_rpm": key_record.rate_limit_rpm,
        "developer_tier": account.tier,
        "account_analytics": analytics,
    }


@router.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    body: EmbeddingRequest,
    auth_data: Tuple[ApiKeyRecord, DeveloperAccount] = Depends(verify_api_key),
):
    """OpenAI-compatible text embeddings endpoint."""
    key_record, account = auth_data
    texts = [body.input] if isinstance(body.input, str) else body.input

    # Generate deterministic 1536-dimensional vector for each input
    import hashlib
    data_list = []
    total_tokens = 0
    for idx, text in enumerate(texts):
        tokens = estimate_tokens(text)
        total_tokens += tokens
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Create 1536 float values normalized
        vector = []
        for i in range(1536):
            b = h[i % len(h)]
            vector.append(round((b / 255.0) * 2 - 1, 6))
        data_list.append(EmbeddingData(index=idx, embedding=vector))

    return EmbeddingResponse(
        data=data_list,
        model=body.model,
        usage=UsageMetrics(prompt_tokens=total_tokens, completion_tokens=0, total_tokens=total_tokens),
    )


# -----------------------------------------------------------------------------
# 2. DEVELOPER DASHBOARD MANAGEMENT ENDPOINTS
# -----------------------------------------------------------------------------

@router.post("/api/developer/keys", response_model=ApiKeyCreatedResponse)
async def create_api_key_endpoint(body: CreateApiKeyRequest):
    """Generate a new CIVORA API key. The raw secret is returned ONLY ONCE."""
    account = dev_db.get_default_account()
    record, raw_key = create_developer_api_key(
        developer_id=account.id,
        name=body.name,
        environment=body.environment,
        rate_limit_rpm=body.rate_limit_rpm or 60,
        quota_monthly=body.quota_monthly or 100000,
        expires_in_days=body.expires_in_days,
    )
    return ApiKeyCreatedResponse(
        id=record.id,
        name=record.name,
        key_prefix=record.key_prefix,
        secret_key=raw_key,
        environment=record.environment,
        rate_limit_rpm=record.rate_limit_rpm,
        quota_monthly=record.quota_monthly,
        created_at=record.created_at,
    )


@router.get("/api/developer/keys", response_model=List[ApiKeySummary])
async def list_api_keys_endpoint():
    """List all API keys belonging to the default developer (masked values only)."""
    account = dev_db.get_default_account()
    records = dev_db.list_api_keys(account.id)
    return [
        ApiKeySummary(
            id=r.id,
            name=r.name,
            key_prefix=r.key_prefix,
            environment=r.environment,
            rate_limit_rpm=r.rate_limit_rpm,
            quota_monthly=r.quota_monthly,
            is_active=r.is_active,
            created_at=r.created_at,
            last_used_at=r.last_used_at,
            expires_at=r.expires_at,
            revoked_at=r.revoked_at,
        )
        for r in records
    ]


@router.post("/api/developer/keys/{key_id}/revoke")
async def revoke_api_key_endpoint(key_id: str):
    """Immediately revoke an API key."""
    account = dev_db.get_default_account()
    success = dev_db.revoke_api_key(key_id, developer_id=account.id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found or already deleted")
    return {"id": key_id, "status": "REVOKED", "revoked": True}


@router.post("/api/developer/keys/{key_id}/regenerate")
async def regenerate_api_key_endpoint(key_id: str):
    """Regenerate/rotate an API key: revokes old key and creates a fresh secret."""
    account = dev_db.get_default_account()
    old_key = dev_db.get_api_key_by_id(key_id)
    if not old_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Revoke old key
    dev_db.revoke_api_key(key_id, developer_id=account.id)

    # Issue new key with same name & environment
    new_record, raw_key = create_developer_api_key(
        developer_id=account.id,
        name=f"{old_key.name} (Rotated)",
        environment=old_key.environment,
        rate_limit_rpm=old_key.rate_limit_rpm,
        quota_monthly=old_key.quota_monthly,
    )
    return {
        "old_key_id": key_id,
        "old_status": "REVOKED",
        "new_key": ApiKeyCreatedResponse(
            id=new_record.id,
            name=new_record.name,
            key_prefix=new_record.key_prefix,
            secret_key=raw_key,
            environment=new_record.environment,
            rate_limit_rpm=new_record.rate_limit_rpm,
            quota_monthly=new_record.quota_monthly,
            created_at=new_record.created_at,
        ),
    }


@router.delete("/api/developer/keys/{key_id}")
async def delete_api_key_endpoint(key_id: str):
    """Permanently delete an API key."""
    account = dev_db.get_default_account()
    success = dev_db.delete_api_key(key_id, developer_id=account.id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"id": key_id, "deleted": True}


@router.get("/api/developer/analytics", response_model=DeveloperAnalyticsResponse)
async def get_developer_analytics_endpoint():
    """Retrieve usage analytics, latency statistics, and request breakdown."""
    account = dev_db.get_default_account()
    analytics = dev_db.get_developer_analytics(account.id)
    return DeveloperAnalyticsResponse(**analytics)


@router.get("/api/developer/account")
async def get_developer_account_endpoint():
    """Retrieve developer account profile and subscription tier."""
    account = dev_db.get_default_account()
    return account.to_dict()
