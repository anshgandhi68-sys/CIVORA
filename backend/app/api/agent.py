"""TrueFoundry Agent Telemetry and Repository Diagnostic Endpoints."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.mcp.tools.repository import repo_get_metadata, repo_list_tree, repo_read_file
from app.mcp.tools.ci import ci_get_workflows, ci_get_check_runs
from app.mcp.tools.documentation import docs_extract_setup_steps

logger = logging.getLogger("civora.api.agent")

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/agent", tags=["TrueFoundry Agent"])


class AgentStatusResponse(BaseModel):
    agent_name: str = "CIVORA ENGINEER"
    runtime: str = "TrueForge / TrueFoundry Agent"
    reasoning_engine: str = "Gemma 4 26B-A4B MoE"
    mcp_endpoint: str = "/mcp"
    mcp_transport: str = "Streamable HTTP (JSON-RPC 2.0 + SSE)"
    zero_trust_header: str = "X-CIVORA-MCP-TOKEN"
    dns_rebinding_protection: bool = True
    read_only_tools_count: int = 6
    read_only_tools: List[str] = [
        "repo_get_metadata",
        "repo_list_tree",
        "repo_read_file",
        "ci_get_workflows",
        "ci_get_check_runs",
        "docs_extract_setup_steps",
    ]
    status: str = "ONLINE"


class AgentInspectRequest(BaseModel):
    owner: str = Field(..., description="Repository owner or organization")
    repo: str = Field(..., description="Repository name")
    ref: Optional[str] = Field(default=None, description="Branch or commit SHA")


class AgentInspectResponse(BaseModel):
    owner: str
    repo: str
    ref: Optional[str]
    agent_name: str = "CIVORA ENGINEER"
    metadata: Dict[str, Any]
    tree: Dict[str, Any]
    docs: Dict[str, Any]
    ci_workflows: Dict[str, Any]
    ci_check_runs: Dict[str, Any]
    status: str = "COMPLETED"


@router.get(
    "/status",
    response_model=AgentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="TrueFoundry Agent Status & MCP Telemetry",
)
async def get_agent_status() -> AgentStatusResponse:
    """Returns the operational status, reasoning engine, and registered MCP tools of the TrueFoundry agent."""
    return AgentStatusResponse(
        mcp_endpoint=settings.MCP_ENDPOINT,
        zero_trust_header=settings.MCP_AUTH_HEADER_NAME,
    )


@router.post(
    "/inspect",
    response_model=AgentInspectResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Live Repository Inspection via MCP Tools",
)
async def inspect_repository(payload: AgentInspectRequest) -> AgentInspectResponse:
    """Executes live read-only inspection using the 6 engineering MCP tools and returns telemetry."""
    owner = payload.owner.strip()
    repo = payload.repo.strip()
    ref = payload.ref.strip() if payload.ref else None

    logger.info("Agent inspecting repository '%s/%s' (ref: %s)", owner, repo, ref or "default")

    # Ingest repository metadata
    metadata = await repo_get_metadata(owner, repo)

    # Ingest file tree
    tree = await repo_list_tree(owner, repo, ref=ref)

    # Extract onboarding commands from documentation
    docs = await docs_extract_setup_steps(owner, repo, ref=ref)

    # Ingest CI workflows & check runs
    workflows = await ci_get_workflows(owner, repo)
    check_runs = await ci_get_check_runs(owner, repo, ref=ref)

    return AgentInspectResponse(
        owner=owner,
        repo=repo,
        ref=ref,
        metadata=metadata,
        tree=tree,
        docs=docs,
        ci_workflows=workflows,
        ci_check_runs=check_runs,
    )
