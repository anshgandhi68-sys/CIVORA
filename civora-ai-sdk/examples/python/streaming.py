#!/usr/bin/env python3
"""CIVORA AI Python Streaming Example.

Demonstrates real-time token streaming using Server-Sent Events (SSE).
"""

import os
import sys
from openai import OpenAI

def main():
    api_key = os.environ.get("CIVORA_API_KEY", "civora_sk_live_YOUR_KEY_HERE")
    base_url = os.environ.get("CIVORA_BASE_URL", "http://localhost:4000/v1")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    print("--- Streaming Live from CIVORA Engineering Agent ---")
    try:
        stream = client.chat.completions.create(
            model="civora-engineering-agent",
            messages=[
                {"role": "user", "content": "Formulate a step-by-step diagnostic verification plan for fixing a broken Docker build."}
            ],
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
        print("\n\n[STREAM COMPLETED]")

    except Exception as e:
        print(f"\n[STREAM ERROR] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
