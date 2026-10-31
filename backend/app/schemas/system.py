"""System Information Pydantic Schemas."""

from typing import List
from pydantic import BaseModel


class SystemInfoResponse(BaseModel):
    project_name: str
    version: str
    environment: str
    mcp_endpoint: str
    mcp_server_name: str
    mcp_server_available: bool = False
    mcp_status: str = "not_mounted"
    allowed_patch_files: List[str]
    sandbox_backend: str
    provenance_enforced: bool = False

