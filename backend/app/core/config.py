"""Application Settings and Configuration."""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    PROJECT_NAME: str = Field(default="CIVORA Core Backend", description="Project name")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version 1 prefix")
    HOST: str = Field(default="0.0.0.0", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port to listen on")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./civora_dev.db",
        description="SQLAlchemy async connection URL",
    )

    # Redis Queue
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    REDIS_ENABLED: bool = Field(
        default=False,
        description="Whether to dispatch runs to real Redis queue or use in-memory task runner",
    )

    # Security
    SECRET_KEY: str = Field(
        default="civora-super-secret-development-key-32-bytes-minimum!",
        description="Secret key for JWT and HMAC tokens",
    )
    ALGORITHM: str = Field(default="HS256", description="Cryptographic algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Token expiry")
    API_KEY_HEADER_NAME: str = Field(default="X-CIVORA-KEY", description="Header name for API key")

    # Model Context Protocol (MCP) Streamable HTTP
    MCP_SERVER_NAME: str = Field(default="civora-engineer", description="MCP Server Name")
    MCP_SERVER_VERSION: str = Field(default="0.1.0", description="MCP Server Version")
    MCP_ENDPOINT: str = Field(default="/mcp", description="Streamable HTTP MCP endpoint")
    MCP_AUTH_TOKEN: str = Field(
        default="civora-mcp-local-dev-token",
        description="Token required to connect TrueForge to the MCP endpoint",
    )

    # GitHub App Credentials
    GITHUB_APP_ID: Optional[str] = Field(default=None, description="GitHub App ID")
    GITHUB_APP_PRIVATE_KEY_PATH: Optional[str] = Field(default=None, description="Path to PEM file")
    GITHUB_APP_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Webhook secret")
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, description="Client ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, description="Client Secret")

    # Sandbox Isolation Policy
    SANDBOX_BACKEND: str = Field(default="simulation", description="Execution backend")
    SANDBOX_TIMEOUT_SECONDS: int = Field(default=300, description="Sandbox max duration")
    SANDBOX_MAX_MEMORY_MB: int = Field(default=2048, description="Memory limit in MB")
    SANDBOX_MAX_CPUS: float = Field(default=2.0, description="CPU core limit")
    SANDBOX_NETWORK_ISOLATION: bool = Field(default=True, description="Enforce network boundaries")
    SANDBOX_RESTRICTED_ROOT: bool = Field(default=True, description="Prohibit root execution")

    # Provenance Engine Policy
    PROVENANCE_HMAC_SECRET: str = Field(
        default="civora-provenance-validation-secret-key-32-bytes",
        description="Secret key for provenance hash generation",
    )
    ALLOWED_PATCH_FILES: List[str] = Field(
        default=["README.md", ".devcontainer/devcontainer.json"],
        description="Strict whitelist of patchable repository files",
    )
    MAX_PATCH_DIFF_LINES: int = Field(default=120, description="Max diff lines permitted per PR")

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("sqlite://"):
            return v.replace("sqlite://", "sqlite+aiosqlite://")
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://")
        return v


settings = Settings()

