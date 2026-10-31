#!/usr/bin/env bash
# CIVORA AI cURL Chat Completion Example

CIVORA_KEY="${CIVORA_API_KEY:-civora_sk_live_YOUR_KEY_HERE}"
CIVORA_URL="${CIVORA_BASE_URL:-http://localhost:4000/v1}"

echo "Dispatching non-streaming completion to ${CIVORA_URL}/chat/completions..."

curl -s -X POST "${CIVORA_URL}/chat/completions" \
  -H "Authorization: Bearer ${CIVORA_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "civora-coder",
    "messages": [
      {"role": "system", "content": "You are CIVORA Senior Coder."},
      {"role": "user", "content": "Write a Python script to verify TLS certificates."}
    ],
    "temperature": 0.7
  }' | jq .
