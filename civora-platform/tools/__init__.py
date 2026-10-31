"""CIVORA Intelligent Tools Package.

Provides 16 verified, typed, and permission-checked tools across 4 categories:
1. Repository (6 tools)
2. Execution (5 tools)
3. Repair (4 tools)
4. Verification (4 tools, total 19 including subroutines)
"""

from .registry import ToolDefinition, ToolParameter, ToolResult, ToolRegistry
from .repository_tools import register_repository_tools
from .execution_tools import register_execution_tools
from .repair_tools import register_repair_tools
from .verification_tools import register_verification_tools


def create_default_registry() -> ToolRegistry:
    """Create and initialize a full registry populated with all tools."""
    registry = ToolRegistry()
    register_repository_tools(registry)
    register_execution_tools(registry)
    register_repair_tools(registry)
    register_verification_tools(registry)
    return registry


__all__ = [
    "ToolDefinition",
    "ToolParameter",
    "ToolResult",
    "ToolRegistry",
    "create_default_registry",
]

