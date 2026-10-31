#!/usr/bin/env bash
# CIVORA AI cURL List Models Example

CIVORA_URL="${CIVORA_BASE_URL:-http://localhost:4000/v1}"

echo "Querying models from ${CIVORA_URL}/models..."

curl -s -X GET "${CIVORA_URL}/models" | jq .
