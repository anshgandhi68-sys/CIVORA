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

