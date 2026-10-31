# CIVORA Core — Backend Service

Autonomous Open-Source Onboarding & Documentation Repair Engine Backend.

## Overview
CIVORA Core provides the high-performance backend foundation and Model Context Protocol (MCP) server that empowers the TrueForge CIVORA ENGINEER agent to inspect repositories, diagnose environment setup failures in isolated sandboxes, verify counterfactual fixes, and propose minimal verified documentation pull requests.

## Architecture
- **Framework**: FastAPI (Python 3.13) with asynchronous I/O and Server-Sent Events (SSE).
- **ORM & Database**: SQLAlchemy 2.0 Async + Alembic with dual PostgreSQL (production) and SQLite (development) support.
- **Model Context Protocol**: Official MCP Python SDK v2 (`mcp==2.3.0`) with Streamable HTTP transport.
- **Job Engine**: Asynchronous decoupled job lifecycle (HTTP 202) backed by Redis.
- **Security**: Zero-Trust Provenance Gate restricting patches strictly to `README.md` and `.devcontainer/devcontainer.json`.

---

## Installation & Development Setup

### 1. Prerequisites
- Python 3.13+
- Homebrew (macOS) or build-essential (Linux)

### 2. Environment Initialization
```bash
# Create and activate virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install pip-tools
pip install --upgrade pip pip-tools

# Install development/test dependencies with hash verification
pip install --require-hashes -r requirements-dev.lock

# Or install production runtime-only dependencies
pip install --require-hashes -r requirements-prod.lock
```

### 3. Environment Variables
Copy `.env.example` to `.env` and configure settings:
```bash
cp .env.example .env
```

Key environment configurations:
- `ENVIRONMENT`: `development` (permits local defaults) or `production` (strictly enforces strong secrets).
- `DATABASE_URL`: `sqlite+aiosqlite:///./civora_dev.db` (local) or `postgresql+asyncpg://user:pass@host/db` (prod).
- `SECRET_KEY`: Cryptographic signing key (minimum 32 characters in production).
- `MCP_AUTH_TOKEN`: Bearer token for TrueForge agent connections (minimum 24 characters in production).
- `PROVENANCE_HMAC_SECRET`: HMAC key for patch integrity audits (minimum 32 characters in production).

---

## Database Migrations

Database schemas are managed using Alembic:

```bash
# Apply migrations to the database
alembic upgrade head

# Generate a new migration revision
alembic revision -m "add_new_feature_table"
```

---

## Running the Test Suite

Execute the comprehensive Pytest test suite:

```bash
# Run all unit and integration tests
pytest -v

# Run with test coverage
pytest --cov=app tests/
```

---

## Starting the Service

Launch the FastAPI development server with Uvicorn:

```bash
# Start on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`
- Liveness Probe: `http://localhost:8000/health`
- Readiness Probe: `http://localhost:8000/health/ready`
- System Info: `http://localhost:8000/api/v1/system/info`
