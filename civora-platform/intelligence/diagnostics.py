"""CIVORA Diagnostics and Root Cause Analysis Engine.

Parses command outputs, execution failures, and stack traces to identify
underlying defect patterns and generate concrete candidate fixes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DiagnosticResult:
    category: str  # MISSING_DEPENDENCY | VERSION_MISMATCH | ENV_MISSING | SYNTAX_ERROR | BUILD_FAILURE | TEST_FAILURE | UNKNOWN
    culprit: str
    confidence: float
    explanation: str
    suggested_action: str
    relevant_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "culprit": self.culprit,
            "confidence": round(self.confidence, 2),
            "explanation": self.explanation,
            "suggested_action": self.suggested_action,
            "relevant_files": self.relevant_files,
        }


class DiagnosticsEngine:
    """Analyzes terminal error logs and identifies root causes."""

    PATTERNS = [
        # Missing Python module
        (
            r"ModuleNotFoundError:\s*No module named\s*['\"]([^'\"]+)['\"]",
            "MISSING_DEPENDENCY",
            0.98,
            "A Python dependency is imported in source code but missing from the runtime environment or requirements.txt.",
            lambda m: f"pip install {m.group(1)} and add {m.group(1)} to requirements.txt",
            ["requirements.txt"],
        ),
        # Node missing module
        (
            r"Cannot find module\s*['\"]([^'\"]+)['\"]",
            "MISSING_DEPENDENCY",
            0.95,
            "A Node.js module was required or imported but is not present in node_modules or package.json.",
            lambda m: f"npm install --save {m.group(1)}",
            ["package.json"],
        ),
        # Missing npm script
        (
            r"npm ERR!\s*missing script:\s*([a-zA-Z0-9_\-]+)",
            "BUILD_FAILURE",
            0.99,
            "The requested npm script does not exist in package.json.",
            lambda m: f"Add '{m.group(1)}' script entry to package.json scripts object.",
            ["package.json"],
        ),
        # Python syntax error
        (
            r"SyntaxError:\s*(.*)\n\s*File\s*['\"]([^'\"]+)['\"],\s*line\s*(\d+)",
            "SYNTAX_ERROR",
            0.95,
            "A syntax error was encountered in Python code.",
            lambda m: f"Fix syntax near line {m.group(3)} in {m.group(2)}: {m.group(1)}",
            lambda m: [m.group(2)],
        ),
        # Missing environment variable
        (
            r"KeyError:\s*['\"]([A-Z0-9_]{3,})['\"]",
            "ENV_MISSING",
            0.85,
            "Code attempted to read an environment variable that is not defined.",
            lambda m: f"Define {m.group(1)} in .env and document in .env.example",
            [".env.example"],
        ),
        # Pytest failure
        (
            r"FAILED\s+([^:]+)::([a-zA-Z0-9_]+)\s*-\s*(.*)",
            "TEST_FAILURE",
            0.90,
            "Automated test assertion failed.",
            lambda m: f"Investigate test assertion failure in {m.group(1)} ({m.group(2)})",
            lambda m: [m.group(1)],
        ),
    ]

    def diagnose(self, stderr: str, stdout: str = "") -> DiagnosticResult:
        full_text = f"{stderr}\n{stdout}"

        for regex, category, conf, desc, action_fn, files in self.PATTERNS:
            match = re.search(regex, full_text, re.MULTILINE)
            if match:
                culprit = match.group(1) if match.groups() else "unknown"
                act = action_fn(match) if callable(action_fn) else str(action_fn)
                rel_files = files(match) if callable(files) else files
                return DiagnosticResult(
                    category=category,
                    culprit=culprit,
                    confidence=conf,
                    explanation=desc,
                    suggested_action=act,
                    relevant_files=rel_files,
                )

        # Fallback heuristic if no specific pattern matched
        if "exit code 1" in full_text.lower() or "error" in full_text.lower():
            return DiagnosticResult(
                category="BUILD_FAILURE",
                culprit="Non-zero exit code during execution",
                confidence=0.60,
                explanation="Subprocess exited with a non-zero code. Error logs indicate an unclassified runtime or build failure.",
                suggested_action="Inspect full terminal output and verify prerequisite dependencies.",
                relevant_files=[],
            )

        return DiagnosticResult(
            category="UNKNOWN",
            culprit="None detected",
            confidence=0.10,
            explanation="No obvious error or defect signature detected in command logs.",
            suggested_action="Proceed with normal execution trace.",
            relevant_files=[],
        )

