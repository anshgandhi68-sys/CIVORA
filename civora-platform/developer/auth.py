"""CIVORA Developer Platform Authentication & Key Cryptography.

Implements cryptographically secure key generation, SHA-256 hashing,
zero-trust key verification, and FastAPI Bearer security dependencies.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import Optional, Tuple

from fastapi import Depends, Header, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import ApiKeyRecord, DeveloperAccount, DeveloperDatabase

# Global DB instance
dev_db = DeveloperDatabase()

# Security scheme
security_bearer = HTTPBearer(auto_error=False)


def generate_raw_secret(length: int = 32) -> str:
    """Generate cryptographically secure random token."""
    return secrets.token_urlsafe(length).replace("-", "").replace("_", "")[:32]


def hash_api_key(raw_key: str) -> str:
    """Compute SHA-256 cryptographic digest of raw API key."""
    return hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()


def mask_api_key(raw_key: str) -> str:
    """Mask key secret for safe dashboard display: civora_sk_live_••••••ab12."""
    if len(raw_key) < 16:
        return "civora_sk_••••••••"
    prefix = raw_key[:15]
    suffix = raw_key[-4:]
    return f"{prefix}••••••{suffix}"


def create_developer_api_key(
    developer_id: str,
    name: str,
    environment: str = "live",
    rate_limit_rpm: int = 60,
    quota_monthly: int = 100000,
    expires_in_days: Optional[int] = None,
) -> Tuple[ApiKeyRecord, str]:
    """Generate and store a new CIVORA API key.
    
    Returns:
        (ApiKeyRecord, raw_key)
        The raw_key MUST be presented to the user once and NEVER logged or stored.
    """
    env_tag = "live" if environment == "live" else "test"
    secret_part = generate_raw_secret(32)
    raw_key = f"civora_sk_{env_tag}_{secret_part}"
    
    key_hash = hash_api_key(raw_key)
    key_prefix = mask_api_key(raw_key)
    key_id = f"key_{secrets.token_hex(6)}"
    
    expires_at = time.time() + (expires_in_days * 86400) if expires_in_days else None

    record = dev_db.insert_api_key(
        key_id=key_id,
        developer_id=developer_id,
        name=name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        environment=env_tag,
        rate_limit_rpm=rate_limit_rpm,
        quota_monthly=quota_monthly,
        expires_at=expires_at,
    )
    return record, raw_key


async def verify_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    api_key_header: Optional[str] = Header(None, alias="X-Civora-Key"),
) -> Tuple[ApiKeyRecord, DeveloperAccount]:
    """FastAPI dependency: authenticates incoming OpenAI-compatible /v1 requests.
    
    Accepts:
        Authorization: Bearer civora_sk_...
        or
        X-Civora-Key: civora_sk_...
    """
    raw_token = None
    if credentials and credentials.credentials:
        raw_token = credentials.credentials.strip()
    elif api_key_header:
        raw_token = api_key_header.strip()

    if not raw_token:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "You didn't provide an API key. You need to provide your API key in an Authorization header using Bearer auth (i.e. 'Authorization: Bearer YOUR_CIVORA_KEY').",
                    "type": "authentication_error",
                    "param": None,
                    "code": "missing_api_key",
                }
            },
        )

    # Validate key format
    if not (raw_token.startswith("civora_sk_live_") or raw_token.startswith("civora_sk_test_")):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Incorrect API key format. CIVORA keys start with 'civora_sk_live_' or 'civora_sk_test_'.",
                    "type": "authentication_error",
                    "param": None,
                    "code": "invalid_api_key_format",
                }
            },
        )

    # Hash and lookup in database
    hashed = hash_api_key(raw_token)
    key_record = dev_db.get_api_key_by_hash(hashed)

    if not key_record:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Incorrect API key provided. Key not found or invalid.",
                    "type": "authentication_error",
                    "param": None,
                    "code": "invalid_api_key",
                }
            },
        )

    # Check active status
    if not key_record.is_active:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "The provided API key has been revoked and cannot be used.",
                    "type": "authentication_error",
                    "param": None,
                    "code": "api_key_revoked",
                }
            },
        )

    # Check expiration
    if key_record.expires_at and time.time() > key_record.expires_at:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "The provided API key has expired.",
                    "type": "authentication_error",
                    "param": None,
                    "code": "api_key_expired",
                }
            },
        )

    # Check monthly quota
    used_tokens = dev_db.get_monthly_token_usage(key_record.id)
    if used_tokens >= key_record.quota_monthly:
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "message": f"Monthly quota exceeded for this API key ({used_tokens}/{key_record.quota_monthly} tokens used). Please upgrade your plan or create a new key.",
                    "type": "rate_limit_error",
                    "param": None,
                    "code": "quota_exceeded",
                }
            },
        )

    # Lookup account
    account = dev_db.get_account(key_record.developer_id)
    if not account:
        account = DeveloperAccount(
            id=key_record.developer_id,
            name="Developer",
            email="dev@civora.ai",
            tier="free",
            created_at=key_record.created_at,
        )

    # Update last used timestamp asynchronously
    dev_db.update_key_last_used(key_record.id)

    return key_record, account
