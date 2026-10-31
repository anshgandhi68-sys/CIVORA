#!/usr/bin/env python3
"""CIVORA AI Python Quickstart Example.

Demonstrates non-streaming chat completions using the standard OpenAI Python client.
"""

import os
import sys
from openai import OpenAI

def main():
    api_key = os.environ.get("CIVORA_API_KEY", "civora_sk_live_YOUR_KEY_HERE")
    base_url = os.environ.get("CIVORA_BASE_URL", "http://localhost:4000/v1")

    print(f"Connecting to CIVORA Universal API at: {base_url}")
    print(f"Using API Key: {api_key[:16]}...")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    prompt = "Explain how Zero-Trust sandbox execution blocks malicious shell injection in CI pipelines."
    print(f"\nUser Query: {prompt}\n")

    try:
        response = client.chat.completions.create(
            model="civora-coder",
            messages=[
                {"role": "system", "content": "You are CIVORA Principal Software Engineer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        print("CIVORA AI Response:\n")
        print(content)

        print("\n--- Telemetry Metrics ---")
        print(f"Prompt Tokens:     {response.usage.prompt_tokens}")
        print(f"Completion Tokens: {response.usage.completion_tokens}")
        print(f"Total Tokens:      {response.usage.total_tokens}")

    except Exception as e:
        print(f"[ERROR] Failed to query CIVORA API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
