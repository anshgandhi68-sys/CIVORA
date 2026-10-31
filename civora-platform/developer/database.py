"""CIVORA Developer Platform Database & Persistence Layer.

Provides SQLite storage for developer accounts, cryptographically hashed API keys,
per-request audit logs, token consumption metrics, and tier subscriptions.
"""

from __future__ import annotations

import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DeveloperAccount:
    id: str
    name: str
    email: str
    tier: str  # 'free', 'pro', 'enterprise'
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "tier": self.tier,
            "created_at": self.created_at,
        }


@dataclass
class ApiKeyRecord:
    id: str
    developer_id: str
    name: str
    key_prefix: str
    key_hash: str
    environment: str  # 'live' or 'test'
    rate_limit_rpm: int
    quota_monthly: int
    is_active: bool
    created_at: float
    last_used_at: Optional[float] = None
    expires_at: Optional[float] = None
    revoked_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "developer_id": self.developer_id,
            "name": self.name,
            "key_prefix": self.key_prefix,
            "environment": self.environment,
            "rate_limit_rpm": self.rate_limit_rpm,
            "quota_monthly": self.quota_monthly,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "expires_at": self.expires_at,
            "revoked_at": self.revoked_at,
        }


class DeveloperDatabase:
    """Thread-safe SQLite manager for developer accounts, keys, and usage tracking."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path).resolve()
        else:
            self.db_path = Path(__file__).parent.parent / "civora_agent.db"
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS developer_accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                tier TEXT DEFAULT 'free',
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                developer_id TEXT NOT NULL,
                name TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                environment TEXT DEFAULT 'live',
                rate_limit_rpm INTEGER DEFAULT 60,
                quota_monthly INTEGER DEFAULT 100000,
                is_active INTEGER DEFAULT 1,
                created_at REAL NOT NULL,
                last_used_at REAL,
                expires_at REAL,
                revoked_at REAL,
                FOREIGN KEY (developer_id) REFERENCES developer_accounts(id)
            );

            CREATE TABLE IF NOT EXISTS api_requests (
                id TEXT PRIMARY KEY,
                key_id TEXT NOT NULL,
                developer_id TEXT NOT NULL,
                model TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                latency_ms REAL DEFAULT 0.0,
                status_code INTEGER DEFAULT 200,
                timestamp REAL NOT NULL,
                ip_address TEXT,
                FOREIGN KEY (key_id) REFERENCES api_keys(id)
            );

            CREATE TABLE IF NOT EXISTS api_usage (
                id TEXT PRIMARY KEY,
                key_id TEXT NOT NULL,
                date TEXT NOT NULL,
                total_requests INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                FOREIGN KEY (key_id) REFERENCES api_keys(id),
                UNIQUE (key_id, date)
            );

            CREATE TABLE IF NOT EXISTS api_subscriptions (
                id TEXT PRIMARY KEY,
                developer_id TEXT NOT NULL,
                plan_tier TEXT DEFAULT 'free',
                monthly_quota_tokens INTEGER DEFAULT 100000,
                rate_limit_rpm INTEGER DEFAULT 60,
                status TEXT DEFAULT 'active',
                created_at REAL NOT NULL,
                FOREIGN KEY (developer_id) REFERENCES developer_accounts(id)
            );

            CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
            CREATE INDEX IF NOT EXISTS idx_api_requests_key ON api_requests(key_id, timestamp);
            """)

            # Ensure default developer account exists
            cur = conn.cursor()
            cur.execute("SELECT id FROM developer_accounts WHERE email = ?", ("developer@civora.ai",))
            if not cur.fetchone():
                dev_id = "dev_default_01"
                conn.execute(
                    "INSERT INTO developer_accounts (id, name, email, tier, created_at) VALUES (?, ?, ?, ?, ?)",
                    (dev_id, "Civora Engineer", "developer@civora.ai", "pro", time.time()),
                )
                conn.execute(
                    "INSERT INTO api_subscriptions (id, developer_id, plan_tier, monthly_quota_tokens, rate_limit_rpm, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (f"sub_{uuid.uuid4().hex[:8]}", dev_id, "pro", 500000, 120, "active", time.time()),
                )

    # -------------------------------------------------------------------------
    # DEVELOPER ACCOUNTS
    # -------------------------------------------------------------------------

    def create_account(self, name: str, email: str, tier: str = "free") -> DeveloperAccount:
        acc_id = f"dev_{uuid.uuid4().hex[:10]}"
        now = time.time()
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO developer_accounts (id, name, email, tier, created_at) VALUES (?, ?, ?, ?, ?)",
                (acc_id, name, email, tier, now),
            )
            # Add subscription
            sub_id = f"sub_{uuid.uuid4().hex[:8]}"
            quota = 500000 if tier == "pro" else (2000000 if tier == "enterprise" else 100000)
            rpm = 120 if tier == "pro" else (300 if tier == "enterprise" else 60)
            conn.execute(
                "INSERT INTO api_subscriptions (id, developer_id, plan_tier, monthly_quota_tokens, rate_limit_rpm, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (sub_id, acc_id, tier, quota, rpm, "active", now),
            )
        return DeveloperAccount(id=acc_id, name=name, email=email, tier=tier, created_at=now)

    def get_account(self, account_id: str) -> Optional[DeveloperAccount]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM developer_accounts WHERE id = ?", (account_id,))
            row = cur.fetchone()
            if not row:
                return None
            return DeveloperAccount(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                tier=row["tier"],
                created_at=row["created_at"],
            )

    def get_default_account(self) -> DeveloperAccount:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM developer_accounts LIMIT 1")
            row = cur.fetchone()
            if row:
                return DeveloperAccount(
                    id=row["id"],
                    name=row["name"],
                    email=row["email"],
                    tier=row["tier"],
                    created_at=row["created_at"],
                )
        return self.create_account("Civora Engineer", "developer@civora.ai", "pro")

    # -------------------------------------------------------------------------
    # API KEYS
    # -------------------------------------------------------------------------

    def insert_api_key(
        self,
        key_id: str,
        developer_id: str,
        name: str,
        key_prefix: str,
        key_hash: str,
        environment: str = "live",
        rate_limit_rpm: int = 60,
        quota_monthly: int = 100000,
        expires_at: Optional[float] = None,
    ) -> ApiKeyRecord:
        now = time.time()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO api_keys (
                    id, developer_id, name, key_prefix, key_hash, environment,
                    rate_limit_rpm, quota_monthly, is_active, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    key_id,
                    developer_id,
                    name,
                    key_prefix,
                    key_hash,
                    environment,
                    rate_limit_rpm,
                    quota_monthly,
                    now,
                    expires_at,
                ),
            )
        return ApiKeyRecord(
            id=key_id,
            developer_id=developer_id,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            environment=environment,
            rate_limit_rpm=rate_limit_rpm,
            quota_monthly=quota_monthly,
            is_active=True,
            created_at=now,
            expires_at=expires_at,
        )

    def get_api_key_by_hash(self, key_hash: str) -> Optional[ApiKeyRecord]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM api_keys WHERE key_hash = ?", (key_hash,))
            row = cur.fetchone()
            if not row:
                return None
            return ApiKeyRecord(
                id=row["id"],
                developer_id=row["developer_id"],
                name=row["name"],
                key_prefix=row["key_prefix"],
                key_hash=row["key_hash"],
                environment=row["environment"],
                rate_limit_rpm=row["rate_limit_rpm"],
                quota_monthly=row["quota_monthly"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_used_at=row["last_used_at"],
                expires_at=row["expires_at"],
                revoked_at=row["revoked_at"],
            )

    def get_api_key_by_id(self, key_id: str) -> Optional[ApiKeyRecord]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM api_keys WHERE id = ?", (key_id,))
            row = cur.fetchone()
            if not row:
                return None
            return ApiKeyRecord(
                id=row["id"],
                developer_id=row["developer_id"],
                name=row["name"],
                key_prefix=row["key_prefix"],
                key_hash=row["key_hash"],
                environment=row["environment"],
                rate_limit_rpm=row["rate_limit_rpm"],
                quota_monthly=row["quota_monthly"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_used_at=row["last_used_at"],
                expires_at=row["expires_at"],
                revoked_at=row["revoked_at"],
            )

    def list_api_keys(self, developer_id: str) -> List[ApiKeyRecord]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM api_keys WHERE developer_id = ? ORDER BY created_at DESC", (developer_id,))
            records = []
            for row in cur.fetchall():
                records.append(
                    ApiKeyRecord(
                        id=row["id"],
                        developer_id=row["developer_id"],
                        name=row["name"],
                        key_prefix=row["key_prefix"],
                        key_hash=row["key_hash"],
                        environment=row["environment"],
                        rate_limit_rpm=row["rate_limit_rpm"],
                        quota_monthly=row["quota_monthly"],
                        is_active=bool(row["is_active"]),
                        created_at=row["created_at"],
                        last_used_at=row["last_used_at"],
                        expires_at=row["expires_at"],
                        revoked_at=row["revoked_at"],
                    )
                )
            return records

    def revoke_api_key(self, key_id: str, developer_id: Optional[str] = None) -> bool:
        now = time.time()
        with self._get_conn() as conn:
            cur = conn.cursor()
            if developer_id:
                cur.execute(
                    "UPDATE api_keys SET is_active = 0, revoked_at = ? WHERE id = ? AND developer_id = ?",
                    (now, key_id, developer_id),
                )
            else:
                cur.execute(
                    "UPDATE api_keys SET is_active = 0, revoked_at = ? WHERE id = ?",
                    (now, key_id),
                )
            return cur.rowcount > 0

    def delete_api_key(self, key_id: str, developer_id: Optional[str] = None) -> bool:
        with self._get_conn() as conn:
            cur = conn.cursor()
            if developer_id:
                cur.execute("DELETE FROM api_keys WHERE id = ? AND developer_id = ?", (key_id, developer_id))
            else:
                cur.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
            return cur.rowcount > 0

    def update_key_last_used(self, key_id: str) -> None:
        with self._get_conn() as conn:
            conn.execute("UPDATE api_keys SET last_used_at = ? WHERE id = ?", (time.time(), key_id))

    # -------------------------------------------------------------------------
    # TELEMETRY & USAGE
    # -------------------------------------------------------------------------

    def record_request(
        self,
        key_id: str,
        developer_id: str,
        model: str,
        endpoint: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        status_code: int = 200,
        ip_address: Optional[str] = None,
    ) -> None:
        now = time.time()
        today = time.strftime("%Y-%m-%d", time.gmtime(now))
        req_id = f"req_{uuid.uuid4().hex[:12]}"
        total_tokens = prompt_tokens + completion_tokens

        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO api_requests (
                    id, key_id, developer_id, model, endpoint,
                    prompt_tokens, completion_tokens, latency_ms,
                    status_code, timestamp, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    req_id,
                    key_id,
                    developer_id,
                    model,
                    endpoint,
                    prompt_tokens,
                    completion_tokens,
                    latency_ms,
                    status_code,
                    now,
                    ip_address,
                ),
            )

            # Upsert daily aggregate usage
            usage_id = f"usg_{key_id}_{today}"
            conn.execute(
                """
                INSERT INTO api_usage (id, key_id, date, total_requests, total_tokens)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(key_id, date) DO UPDATE SET
                    total_requests = total_requests + 1,
                    total_tokens = total_tokens + excluded.total_tokens
                """,
                (usage_id, key_id, today, total_tokens),
            )

    def get_monthly_token_usage(self, key_id: str) -> int:
        # Sum token usage for current month (current 30 days)
        since_ts = time.time() - (30 * 86400)
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT SUM(prompt_tokens + completion_tokens) as total FROM api_requests WHERE key_id = ? AND timestamp >= ?",
                (key_id, since_ts),
            )
            row = cur.fetchone()
            return int(row["total"] or 0) if row else 0

    def get_developer_analytics(self, developer_id: str) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status_code >= 200 AND status_code < 400 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as failed_requests,
                    SUM(prompt_tokens) as total_prompt_tokens,
                    SUM(completion_tokens) as total_completion_tokens,
                    AVG(latency_ms) as avg_latency_ms
                FROM api_requests
                WHERE developer_id = ?
                """,
                (developer_id,),
            )
            agg = cur.fetchone()

            # Breakdown by model
            cur.execute(
                """
                SELECT model, COUNT(*) as count, SUM(prompt_tokens + completion_tokens) as tokens
                FROM api_requests
                WHERE developer_id = ?
                GROUP BY model
                ORDER BY count DESC
                """,
                (developer_id,),
            )
            models = [{"model": r["model"], "requests": r["count"], "tokens": r["tokens"] or 0} for r in cur.fetchall()]

            # Recent requests
            cur.execute(
                """
                SELECT id, model, endpoint, prompt_tokens, completion_tokens, latency_ms, status_code, timestamp
                FROM api_requests
                WHERE developer_id = ?
                ORDER BY timestamp DESC
                LIMIT 20
                """,
                (developer_id,),
            )
            recent_requests = [dict(r) for r in cur.fetchall()]

            return {
                "total_requests": agg["total_requests"] or 0,
                "successful_requests": agg["successful_requests"] or 0,
                "failed_requests": agg["failed_requests"] or 0,
                "total_prompt_tokens": agg["total_prompt_tokens"] or 0,
                "total_completion_tokens": agg["total_completion_tokens"] or 0,
                "total_tokens": (agg["total_prompt_tokens"] or 0) + (agg["total_completion_tokens"] or 0),
                "avg_latency_ms": round(agg["avg_latency_ms"] or 0.0, 1),
                "models_breakdown": models,
                "recent_requests": recent_requests,
            }
