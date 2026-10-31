"""Unit Tests for Configuration and Settings."""

from app.core.config import Settings


def test_default_settings():
    """Verify default settings initialization."""
    settings = Settings()
    assert settings.PROJECT_NAME == "CIVORA Core Backend"
    assert settings.ENVIRONMENT in ["development", "test", "production"]
    assert settings.API_V1_PREFIX == "/api/v1"
    assert "README.md" in settings.ALLOWED_PATCH_FILES
    assert ".devcontainer/devcontainer.json" in settings.ALLOWED_PATCH_FILES


def test_database_url_validation():
    """Verify sqlite:// and postgresql:// URL prefix auto-correction for async drivers."""
    s1 = Settings(DATABASE_URL="sqlite:///./test.db")
    assert s1.DATABASE_URL == "sqlite+aiosqlite:///./test.db"

    s2 = Settings(DATABASE_URL="postgresql://user:pass@localhost:5432/db")
    assert s2.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/db"


def test_cors_origins_type():
    """Verify CORS origins list configuration."""
    settings = Settings(BACKEND_CORS_ORIGINS=["http://test.com"])
    assert "http://test.com" in settings.BACKEND_CORS_ORIGINS


def test_production_secrets_valid():
    """Verify that strong, unique secrets pass production validation."""
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="c" * 32,
        MCP_AUTH_TOKEN="m" * 24,
        PROVENANCE_HMAC_SECRET="p" * 32,
    )
    assert prod_settings.ENVIRONMENT == "production"
    assert prod_settings.SECRET_KEY == "c" * 32
    assert prod_settings.MCP_AUTH_TOKEN == "m" * 24
    assert prod_settings.PROVENANCE_HMAC_SECRET == "p" * 32


def test_production_rejects_insecure_default_secret_key():
    """Verify production rejects known development default SECRET_KEY."""
    import pytest
    with pytest.raises(ValueError, match="Known development default SECRET_KEY is strictly prohibited"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="civora-super-secret-development-key-32-bytes-minimum!",
            MCP_AUTH_TOKEN="m" * 24,
            PROVENANCE_HMAC_SECRET="p" * 32,
        )


def test_production_rejects_short_secret_key():
    """Verify production rejects SECRET_KEY shorter than 32 characters."""
    import pytest
    with pytest.raises(ValueError, match="requires a strong SECRET_KEY with at least 32 characters"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short-secret-key",
            MCP_AUTH_TOKEN="m" * 24,
            PROVENANCE_HMAC_SECRET="p" * 32,
        )


def test_production_rejects_insecure_default_mcp_token():
    """Verify production rejects known development default MCP_AUTH_TOKEN."""
    import pytest
    with pytest.raises(ValueError, match="Known development default MCP_AUTH_TOKEN is strictly prohibited"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="c" * 32,
            MCP_AUTH_TOKEN="civora-mcp-local-dev-token",
            PROVENANCE_HMAC_SECRET="p" * 32,
        )


def test_production_rejects_short_mcp_token():
    """Verify production rejects MCP_AUTH_TOKEN shorter than 24 characters."""
    import pytest
    with pytest.raises(ValueError, match="requires a strong MCP_AUTH_TOKEN with at least 24 characters"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="c" * 32,
            MCP_AUTH_TOKEN="short-token",
            PROVENANCE_HMAC_SECRET="p" * 32,
        )


def test_production_rejects_insecure_default_hmac_secret():
    """Verify production rejects known development default PROVENANCE_HMAC_SECRET."""
    import pytest
    with pytest.raises(ValueError, match="Known development default PROVENANCE_HMAC_SECRET is strictly prohibited"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="c" * 32,
            MCP_AUTH_TOKEN="m" * 24,
            PROVENANCE_HMAC_SECRET="civora-provenance-validation-secret-key-32-bytes",
        )


def test_production_rejects_short_hmac_secret():
    """Verify production rejects PROVENANCE_HMAC_SECRET shorter than 32 characters."""
    import pytest
    with pytest.raises(ValueError, match="requires a strong PROVENANCE_HMAC_SECRET with at least 32 characters"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="c" * 32,
            MCP_AUTH_TOKEN="m" * 24,
            PROVENANCE_HMAC_SECRET="short-hmac-secret",
        )

