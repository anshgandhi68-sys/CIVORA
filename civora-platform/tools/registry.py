"""CIVORA Tool Registry and Schemas.

Defines standard schemas, parameter contracts, execution constraints,
and structured outputs for all autonomous agent tools.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }


@dataclass
class ToolDefinition:
    name: str
    category: str  # repository | execution | repair | verification
    description: str
    parameters: List[ToolParameter]
    handler: Callable[..., ToolResult]
    requires_sandbox: bool = True

    def to_schema(self) -> Dict[str, Any]:
        """Export tool schema compatible with LLM function calling."""
        props = {}
        required = []
        for p in self.parameters:
            props[p.name] = {
                "type": p.type,
                "description": p.description,
            }
            if p.required:
                required.append(p.name)

        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        }


class ToolRegistry:
    """Central registry of verified tools available to the AI Orchestrator."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_all(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def list_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(
                tool_name=name,
                success=False,
                data=None,
                error=f"Tool '{name}' is not registered in the CIVORA tool registry.",
            )

        try:
            # Validate required parameters
            for param in tool.parameters:
                if param.required and param.name not in kwargs and param.default is None:
                    return ToolResult(
                        tool_name=name,
                        success=False,
                        data=None,
                        error=f"Missing required parameter '{param.name}' for tool '{name}'.",
                    )
            return tool.handler(**kwargs)
        except Exception as exc:
            return ToolResult(
                tool_name=name,
                success=False,
                data=None,
                error=f"Execution error in tool '{name}': {str(exc)}",
            )

