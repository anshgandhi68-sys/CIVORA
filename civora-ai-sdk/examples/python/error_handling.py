#!/usr/bin/env python3
"""CIVORA AI Error Handling & Rate Limiting Example.

Demonstrates catching authentication, format, and rate-limit errors.
"""

from openai import OpenAI, AuthenticationError, RateLimitError

def test_invalid_key():
    print("1. Testing Invalid API Key Handling...")
    client = OpenAI(
        api_key="civora_sk_live_00000000000000000000000000000000",
        base_url="http://localhost:4000/v1"
    )
    try:
        client.chat.completions.create(
            model="civora-coder",
            messages=[{"role": "user", "content": "hello"}]
        )
    except AuthenticationError as e:
        print(f"Caught expected AuthenticationError: {e}\n")

def test_malformed_key():
    print("2. Testing Malformed Key Prefix Handling...")
    client = OpenAI(
        api_key="sk-openai-key-which-is-not-civora",
        base_url="http://localhost:4000/v1"
    )
    try:
        client.chat.completions.create(
            model="civora-coder",
            messages=[{"role": "user", "content": "hello"}]
        )
    except AuthenticationError as e:
        print(f"Caught expected KeyFormatError: {e}\n")

if __name__ == "__main__":
    test_invalid_key()
    test_malformed_key()
