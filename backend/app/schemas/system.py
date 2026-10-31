"""System Information Pydantic Schemas."""

from typing import List
from pydantic import BaseModel


class SystemInfoResponse(BaseModel):
    project_name: str
    version: str
    environment: str
    mcp_endpoint: str
    mcp_server_name: str
    mcp_server_available: bool = True
    mcp_status: str = "mounted_read_only"
    github_integration_available: bool = False
    github_integration_status: str = "not_configured"
    allowed_patch_files: List[str]
    sandbox_backend: str
    provenance_enforced: bool = False

