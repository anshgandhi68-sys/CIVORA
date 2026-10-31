#!/usr/bin/env python3
"""CIVORA AI Repository Agent Example.

Demonstrates querying the workspace-aware model for repository drift and file architecture.
"""

import os
from openai import OpenAI

def main():
    client = OpenAI(
        api_key=os.environ.get("CIVORA_API_KEY", "civora_sk_live_YOUR_KEY_HERE"),
        base_url=os.environ.get("CIVORA_BASE_URL", "http://localhost:4000/v1")
    )

    response = client.chat.completions.create(
        model="civora-repository-agent",
        messages=[
            {"role": "user", "content": "What documentation drift issues currently exist between our package manifests and README?"}
        ]
    )

    print("CIVORA Repository Intelligence:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
