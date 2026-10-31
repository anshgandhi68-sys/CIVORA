# CIVORA AI Universal SDK & Developer Platform

> **CIVORA API — Your AI Engineering Intelligence, Everywhere.**

Welcome to the official developer repository for **CIVORA API**. Access CIVORA's autonomous software engineering intelligence, documentation drift radar, and zero-trust sandbox execution from any laptop, programming language, IDE, or LLM client that supports OpenAI-compatible endpoints.

---

## ⚡ Quick Navigation

- [1. Universal API Keys & Authentication](#1-universal-api-keys--authentication)
- [2. Available CIVORA Models](#2-available-civora-models)
- [3. Python Quickstart (`openai` SDK)](#3-python-quickstart)
- [4. JavaScript & Node.js Quickstart (`openai` npm)](#4-javascript--nodejs-quickstart)
- [5. TypeScript Integration](#5-typescript-integration)
- [6. cURL Examples](#6-curl-examples)
- [7. Cursor & VS Code Setup](#7-cursor--vs-code-setup)
- [8. Rate Limits, Quotas & Error Schemas](#8-rate-limits-quotas--error-schemas)
- [9. Zero-Trust Security Policies](#9-zero-trust-security-policies)

---

## 1. Universal API Keys & Authentication

Every CIVORA API key is generated using cryptographically secure entropy and stored exclusively as an irreversible **SHA-256 hash**. Raw keys are presented only once during creation.

### Key Format
- **Live / Production:** `civora_sk_live_<32-character-random-secret>`
- **Test / Sandbox:** `civora_sk_test_<32-character-random-secret>`

### Header Authentication
All `/v1` requests require the standard `Authorization` header:

```http
Authorization: Bearer civora_sk_live_YOUR_KEY_HERE
```

*(Alternatively, the `X-Civora-Key` header is also accepted).*

---

## 2. Available CIVORA Models

| Model Identifier | Specialization | Capabilities |
| :--- | :--- | :--- |
| **`civora-coder`** | Senior Polyglot Engineer | AST-level code generation, bug fixing, test synthesis, and refactoring. |
| **`civora-general`** | Principal Systems Architect | High-level system design, algorithm analysis, distributed architectures. |
| **`civora-repository-agent`** | Workspace & Drift Intelligence | Deep workspace structure awareness, manifest drift detection, env audit. |
| **`civora-engineering-agent`** | Autonomous Reasoning Loop | Multi-stage diagnosis, zero-trust sandbox verification, and patch proofs. |

---

## 3. Python Quickstart

CIVORA is 100% drop-in compatible with the official OpenAI Python library (`pip install openai`).

```python
import os
from openai import OpenAI

# Initialize client pointing to CIVORA API
client = OpenAI(
    api_key=os.environ.get("CIVORA_API_KEY", "civora_sk_live_YOUR_KEY_HERE"),
    base_url="http://localhost:4000/v1"  # Or your deployed CIVORA domain
)

# 1. Non-Streaming Chat Completion
completion = client.chat.completions.create(
    model="civora-coder",
    messages=[
        {"role": "system", "content": "You are a Principal Software Engineer."},
        {"role": "user", "content": "Write a thread-safe token bucket rate limiter in Python."}
    ],
    temperature=0.7,
)

print("CIVORA Response:\n", completion.choices[0].message.content)
print(f"\nTokens Consumed: {completion.usage.total_tokens}")

# 2. Real-Time Streaming Completion (Server-Sent Events)
stream = client.chat.completions.create(
    model="civora-repository-agent",
    messages=[
        {"role": "user", "content": "Audit the repository structure and describe drift issues."}
    ],
    stream=True,
)

print("\n--- Live Streaming Trace ---")
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
```

---

## 4. JavaScript & Node.js Quickstart

Compatible with Node.js 18+, modern browser runtimes, Next.js, and Bun:

```bash
npm install openai
```

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.CIVORA_API_KEY || "civora_sk_live_YOUR_KEY_HERE",
  baseURL: "http://localhost:4000/v1"
});

async function main() {
  const completion = await client.chat.completions.create({
    model: "civora-engineering-agent",
    messages: [
      { role: "user", content: "Diagnose why npm test fails when lockfile is missing." }
    ]
  });

  console.log("CIVORA Solution:\n", completion.choices[0].message.content);
}

main().catch(console.error);
```

---

## 5. TypeScript Integration

Strictly typed example with type safety:

```typescript
import OpenAI from "openai";

const civora = new OpenAI({
  apiKey: process.env.CIVORA_API_KEY!,
  baseURL: "http://localhost:4000/v1"
});

async function runAudit(query: string): Promise<string> {
  const response = await civora.chat.completions.create({
    model: "civora-repository-agent",
    messages: [{ role: "user", content: query }],
    temperature: 0.5,
  });

  return response.choices[0]?.message?.content ?? "";
}
```

---

## 6. cURL Examples

### List Models
```bash
curl -X GET http://localhost:4000/v1/models
```

### Chat Completion (Sync)
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer civora_sk_live_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "civora-coder",
    "messages": [
      {"role": "user", "content": "Explain how AST parsing detects documentation drift."}
    ],
    "temperature": 0.7
  }'
```

### Chat Completion (Streaming)
```bash
curl -N -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer civora_sk_live_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "civora-general",
    "messages": [{"role": "user", "content": "Explain clean-room verification."}],
    "stream": true
  }'
```

---

## 7. Cursor & VS Code Setup

### Cursor IDE
1. Open Cursor **Settings** (`Cmd + ,` on macOS, `Ctrl + ,` on Windows/Linux).
2. Click **Models** in the sidebar.
3. Enable **OpenAI API Key** and paste your `civora_sk_live_...` key.
4. Enable **Override OpenAI Base URL** and enter:
   ```
   http://localhost:4000/v1
   ```
5. Under model list, add `civora-coder` and `civora-engineering-agent`.

### VS Code (Continue / Cline)
In `~/.continue/config.json`:
```json
{
  "models": [
    {
      "title": "CIVORA Coder",
      "provider": "openai",
      "model": "civora-coder",
      "apiKey": "civora_sk_live_...",
      "apiBase": "http://localhost:4000/v1"
    }
  ]
}
```

---

## 8. Rate Limits, Quotas & Error Schemas

All API responses return standard rate limit headers:
- `x-ratelimit-limit-requests`: Maximum permitted requests per minute (RPM).
- `x-ratelimit-remaining-requests`: Remaining requests in current sliding window.
- `x-ratelimit-reset-requests`: Seconds until window reset.

### Error Response Schema
```json
{
  "error": {
    "message": "Rate limit reached for requests: 60 requests per minute. Please back off.",
    "type": "rate_limit_error",
    "param": null,
    "code": "rate_limit_exceeded"
  }
}
```

Standard error codes:
- `missing_api_key` (HTTP 401)
- `invalid_api_key_format` (HTTP 401)
- `invalid_api_key` (HTTP 401)
- `api_key_revoked` (HTTP 401)
- `api_key_expired` (HTTP 401)
- `quota_exceeded` (HTTP 429)
- `rate_limit_exceeded` (HTTP 429)

---

## 9. Zero-Trust Security Policies

1. **Zero Secret Logging:** Raw API keys are never printed to terminal logs, audit logs, or error traces.
2. **Cryptographic Hashes Only:** The database stores only SHA-256 digests. Compromising the database yields zero plaintext credentials.
3. **Immediate Revocation:** Revoked keys are rejected at the edge dependency layer in sub-millisecond time.
4. **Isolated Workspaces:** Public chat completions cannot trigger arbitrary host commands. Execution is confined to the Zero-Trust sandbox with strict whitelisting.

---

© 2026 CIVORA AI. All Rights Reserved.

