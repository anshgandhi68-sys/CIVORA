"""System Information Pydantic Schemas."""

from typing import List
from pydantic import BaseModel


class SystemInfoResponse(BaseModel):
    project_name: str
    version: str
    environment: str
    mcp_endpoint: str
    mcp_server_name: str
    allowed_patch_files: List[str]
    sandbox_backend: str
    provenance_enforced: bool = False

