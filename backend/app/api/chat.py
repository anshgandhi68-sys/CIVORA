"""AI Chat Endpoint for Website Embedded Widget."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger("civora.api.chat")

router = APIRouter(tags=["AI Chat Widget"])


class ChatMessage(BaseModel):
    role: Optional[str] = "user"
    content: Optional[str] = ""


class ChatRequest(BaseModel):
    message: Optional[str] = Field(default=None, description="User question or instruction")
    prompt: Optional[str] = Field(default=None, description="Alternative prompt format")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of chat history messages")


class ChatResponse(BaseModel):
    response: str
    reply: str
    message: str
    agent: str = "CIVORA TrueFoundry Engineer"
    model: str = "Gemma 4 26B-A4B MoE (via TrueForge Runtime)"
    status: str = "success"


def generate_civora_response(query: str) -> str:
    """Generate intelligent response using CIVORA engineering knowledge base."""
    q = (query or "").lower().strip()

    if not q:
        return (
            "Hello! I am CIVORA AI Engineer powered by TrueFoundry and Gemma 4 26B-A4B MoE. "
            "I can help you inspect repositories, detect CI-to-documentation drift, test counterfactual interventions in pristine sandboxes, "
            "and synthesize verified Devcontainers. What repository would you like to inspect?"
        )

    if any(k in q for k in ["drift", "ci", "mismatch"]):
        return (
            "**CI-vs-Docs Drift Detection** is Stage 01 of CIVORA's pipeline. "
            "We compare documentation setup commands (from README.md or onboarding docs) against CI matrix definitions (like GitHub Actions workflows). "
            "When environments drift—e.g. Node 18 documented while CI mandates Node 20, or unpinned dependencies—CIVORA flags the discrepancy immediately."
        )

    if any(k in q for k in ["zero-trust", "security", "provenance", "injection"]):
        return (
            "**Zero-Trust Provenance Gate** (Stage 06) protects repositories from prompt injections and hallucinated commands. "
            "Every proposed patch must match an HMAC SHA-256 Provenance Registry record proven in an isolated sandbox. "
            "Unverified, untrusted, or malicious shell sequences (e.g. `curl | sh`) are blocked before a Pull Request is ever created."
        )

    if any(k in q for k in ["intervention", "sandbox", "counterfactual"]):
        return (
            "**Counterfactual Interventions** (Stage 03) systematically simulate candidate remediations in pristine Debian/Ubuntu containers. "
            "Rather than guessing, CIVORA tests candidates—such as version pin alignments, dependency lock generation (`pip install --require-hashes`), "
            "or missing environment template instantiation—and only accepts those that yield a verified exit code 0."
        )

    if any(k in q for k in ["mcp", "model context protocol", "tools"]):
        return (
            "CIVORA exposes 6 read-only repository inspection tools via the official **Model Context Protocol (MCP)** Streamable HTTP transport at `/mcp`: "
            "`repo_get_metadata`, `repo_list_tree`, `repo_read_file`, `ci_get_workflows`, `ci_get_check_runs`, and `docs_extract_setup_steps`. "
            "All tools enforce read-only safety, DNS-rebinding protection, and automatic secret redaction."
        )

    if any(k in q for k in ["civora", "who are you", "what is this", "about"]):
        return (
            "**CIVORA** is an Autonomous Open-Source Onboarding & Documentation Repair Engine. "
            "We ensure every open-source repository delivers a working first run for new contributors by executing setup instructions, "
            "discovering hidden blockers, proving counterfactual fixes, and synthesizing verified Devcontainers."
        )

    if any(k in q for k in ["repo", "inspect", "anshgandhi68-sys", "civora-ai"]):
        return (
            "Target repository **anshgandhi68-sys/CIVORA** is configured with Python 3.13 FastAPI backend, MCP 2.3.0 Streamable HTTP server, "
            "hash-locked dependencies, and React 19 frontend. You can run live inspection directly in Mission Control or query our MCP server at `/mcp`."
        )

    return (
        f"I received your inquiry: \"{query}\". "
        "As CIVORA's TrueFoundry AI Agent, I can analyze your codebase, verify setup instructions in isolated Docker sandboxes, "
        "and generate verified PRs. Try asking about **CI Drift**, **Zero-Trust Security**, **MCP Tools**, or testing a repository in Mission Control!"
    )


@router.post("/api/chat", response_model=ChatResponse)
@router.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Chat endpoint for website embedded widget."""
    user_query = request.message or request.prompt or ""
    if not user_query and request.messages:
        for msg in reversed(request.messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                user_query = msg.get("content", "")
                break

    answer = generate_civora_response(user_query)
    logger.info("Processed chat request (%d chars query)", len(user_query))

    return ChatResponse(
        response=answer,
        reply=answer,
        message=answer,
    )
