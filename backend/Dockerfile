# Production Dockerfile for CIVORA Core Backend
FROM python:3.13-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# System dependencies for cryptography and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd -g 1001 civora && useradd -u 1001 -g civora -s /bin/bash -m civora

WORKDIR /app

# Install production Python dependencies with strict SHA-256 hash verification
COPY requirements-prod.lock .
RUN pip install --no-cache-dir --require-hashes -r requirements-prod.lock

# Copy backend application code
COPY . .

RUN chown -R civora:civora /app
USER civora

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

