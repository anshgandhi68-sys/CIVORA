"""CIVORA Developer Platform Pydantic Schemas.

Complies strictly with the OpenAI v1 Chat Completions, Models, and Embeddings specifications,
along with developer account and key management schemas.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# OPENAI-COMPATIBLE SCHEMAS
# -----------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "function", "tool"] = "user"
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="CIVORA model identifier (e.g. civora-coder, civora-general, civora-repository-agent, civora-engineering-agent)")
    messages: List[ChatMessage] = Field(..., description="Array of chat conversation messages")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(2048, ge=1, le=8192)
    stream: Optional[bool] = Field(False, description="Whether to stream responses using Server-Sent Events (SSE)")
    user: Optional[str] = None


class ChatCompletionChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChatCompletionChoiceMessage
    finish_reason: Optional[str] = "stop"


class UsageMetrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: UsageMetrics
    system_fingerprint: Optional[str] = "fp_civora_v2"


class ChatCompletionChunkDelta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionChunkChoice(BaseModel):
    index: int = 0
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChunkChoice]


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = 1730300000
    owned_by: str = "civora-ai"
    permission: List[Dict[str, Any]] = []
    root: Optional[str] = None
    parent: Optional[str] = None
    description: Optional[str] = None


class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelCard]


class EmbeddingRequest(BaseModel):
    model: str = "civora-embeddings"
    input: Union[str, List[str]]
    user: Optional[str] = None


class EmbeddingData(BaseModel):
    object: str = "embedding"
    index: int = 0
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: UsageMetrics


# -----------------------------------------------------------------------------
# DEVELOPER MANAGEMENT SCHEMAS
# -----------------------------------------------------------------------------

class CreateApiKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Friendly label for the API key")
    environment: Literal["live", "test"] = "live"
    rate_limit_rpm: Optional[int] = Field(60, ge=5, le=600)
    quota_monthly: Optional[int] = Field(100000, ge=1000, le=10000000)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class ApiKeyCreatedResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    secret_key: str = Field(..., description="Full secret key. Presented only once! Never logged or stored raw.")
    environment: str
    rate_limit_rpm: int
    quota_monthly: int
    created_at: float
    warning: str = "Make sure to copy your API key now. You will not be able to see it again!"


class ApiKeySummary(BaseModel):
    id: str
    name: str
    key_prefix: str
    environment: str
    rate_limit_rpm: int
    quota_monthly: int
    is_active: bool
    created_at: float
    last_used_at: Optional[float] = None
    expires_at: Optional[float] = None
    revoked_at: Optional[float] = None


class DeveloperAnalyticsResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    avg_latency_ms: float
    models_breakdown: List[Dict[str, Any]]
    recent_requests: List[Dict[str, Any]]
