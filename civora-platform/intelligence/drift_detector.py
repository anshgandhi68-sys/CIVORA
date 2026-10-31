"""CIVORA Documentation Drift Detection Engine.

Compares repository README instructions against actual manifests,
CI workflows, environment configurations, and build scripts.
Identifies broken setup commands, missing dependencies, version drifts,
and undeclared environment variables.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .repo_scanner import RepoScanner, RepoIntelligenceSummary


@dataclass
class DriftFinding:
    id: str
    title: str
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    category: str  # VERSION_MISMATCH | OUTDATED_INSTALL | MISSING_DEPENDENCY | MISSING_ENV_VAR | BUILD_MISMATCH | PREREQUISITE_MISSING
    affected_files: List[str]
    explanation: str
    evidence: str
    suggested_fix: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "category": self.category,
            "affected_files": self.affected_files,
            "explanation": self.explanation,
            "evidence": self.evidence,
            "suggested_fix": self.suggested_fix,
        }


class DriftDetector:
    """Detects disparities between written documentation and actual code reality."""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()

    def analyze(self, summary: Optional[RepoIntelligenceSummary] = None) -> List[DriftFinding]:
        if not summary:
            scanner = RepoScanner(str(self.workspace_path))
            summary = scanner.scan()

        findings: List[DriftFinding] = []

        # 1. Check for Missing README
        if not summary.readme_content:
            findings.append(DriftFinding(
                id="DRIFT-001",
                title="Missing Repository Documentation (README.md)",
                severity="HIGH",
                category="PREREQUISITE_MISSING",
                affected_files=["README.md"],
                explanation="No README.md found in the root directory. Prospective contributors cannot set up or run the project.",
                evidence="Directory scan of root found 0 markdown documentation files.",
                suggested_fix="Generate a standard README.md with setup, installation, and build instructions.",
            ))
            return findings

        # 2. Check Package Manager / Outdated Install Command Drift
        has_pnpm_lock = (self.workspace_path / "pnpm-lock.yaml").exists()
        has_yarn_lock = (self.workspace_path / "yarn.lock").exists()
        has_package_lock = (self.workspace_path / "package-lock.json").exists()

        for inst in summary.readme_instructions.get("install", []):
            if "npm install" in inst and has_pnpm_lock:
                findings.append(DriftFinding(
                    id="DRIFT-002",
                    title="Package Manager Command Drift (pnpm vs npm)",
                    severity="HIGH",
                    category="OUTDATED_INSTALL",
                    affected_files=["README.md", "pnpm-lock.yaml"],
                    explanation="README prescribes 'npm install', but repository contains 'pnpm-lock.yaml'. Running npm can corrupt the lockfile or fail to install hoisted dependencies.",
                    evidence=f"README command: '{inst}' | Lockfile detected: pnpm-lock.yaml",
                    suggested_fix="Update README.md to instruct 'pnpm install' or document Corepack setup.",
                ))
            elif "npm install" in inst and has_yarn_lock:
                findings.append(DriftFinding(
                    id="DRIFT-003",
                    title="Package Manager Command Drift (yarn vs npm)",
                    severity="MEDIUM",
                    category="OUTDATED_INSTALL",
                    affected_files=["README.md", "yarn.lock"],
                    explanation="README prescribes 'npm install', but repository uses Yarn lockfile.",
                    evidence=f"README command: '{inst}' | Lockfile detected: yarn.lock",
                    suggested_fix="Update README.md to instruct 'yarn install'.",
                ))

        # 3. Check for Build Script Mismatch
        pkg_data = summary.manifests.get("package.json", {})
        scripts = pkg_data.get("scripts", {})
        for build_cmd in summary.readme_instructions.get("build", []):
            if "npm run build" in build_cmd and "build" not in scripts:
                findings.append(DriftFinding(
                    id="DRIFT-004",
                    title="Non-existent Build Script in Documentation",
                    severity="CRITICAL",
                    category="BUILD_MISMATCH",
                    affected_files=["README.md", "package.json"],
                    explanation="README instructs users to run 'npm run build', but 'package.json' has no 'build' script defined. Contributor execution will fail with exit code 1.",
                    evidence=f"README instruction: '{build_cmd}' | Available scripts in package.json: {list(scripts.keys())}",
                    suggested_fix="Add the 'build' script to package.json or update README.md to the correct command.",
                ))

        # 4. Check for Test Script Mismatch
        for test_cmd in summary.readme_instructions.get("test", []):
            if "npm test" in test_cmd and ("test" not in scripts or scripts.get("test") == 'echo "Error: no test specified" && exit 1'):
                findings.append(DriftFinding(
                    id="DRIFT-005",
                    title="Broken Test Command in Documentation",
                    severity="HIGH",
                    category="BUILD_MISMATCH",
                    affected_files=["README.md", "package.json"],
                    explanation="README tells developers to run 'npm test', but package.json has no test runner configured or retains the default exit 1 placeholder.",
                    evidence=f"package.json test script: '{scripts.get('test', 'NOT_FOUND')}'",
                    suggested_fix="Configure a valid test runner (e.g. vitest, jest) or remove test instructions from README until implemented.",
                ))

        # 5. Check Undeclared Environment Variables (Code vs .env.example)
        detected_env_vars = set(summary.env_variables_detected)
        declared_env_vars: set[str] = set()
        
        env_example_paths = [p for p in (self.workspace_path / ".env.example", self.workspace_path / ".env.sample") if p.exists()]
        if env_example_paths:
            for env_path in env_example_paths:
                try:
                    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            var_name = line.split("=")[0].strip()
                            declared_env_vars.add(var_name)
                except Exception:
                    pass
        
        # Look for undeclared critical env vars
        missing_vars = []
        for var in detected_env_vars:
            # ignore standard system env vars
            if var in ("PATH", "NODE_ENV", "PORT", "HOST", "DEBUG", "HOME", "USER"):
                continue
            if var not in declared_env_vars and not any(var in (summary.readme_content or "") for _ in [1]):
                missing_vars.append(var)

        if missing_vars:
            findings.append(DriftFinding(
                id="DRIFT-006",
                title=f"Undeclared Environment Variables ({len(missing_vars)} missing from .env.example)",
                severity="HIGH",
                category="MISSING_ENV_VAR",
                affected_files=[".env.example"] if env_example_paths else ["README.md", ".env.example"],
                explanation=f"Source code references environment variables ({', '.join(missing_vars[:5])}) that are not documented in .env.example or README. New developers will encounter runtime crashes.",
                evidence=f"Referenced in code: {missing_vars[:10]} | Declared in .env.example: {list(declared_env_vars)}",
                suggested_fix=f"Document all required environment variables with example dummy values in .env.example:\n" + "\n".join(f"{v}=your_{v.lower()}_here" for v in missing_vars[:5]),
            ))

        # 6. Check Python Dependency Drift (Imports vs requirements.txt)
        if "requirements.txt" in summary.manifests:
            req_pkgs = set(p.split("==")[0].split(">=")[0].strip().lower() for p in summary.manifests["requirements.txt"])
            # Check if common imports in python files are missing from requirements.txt
            missing_imports = set()
            for py_file in self.workspace_path.rglob("*.py"):
                if any(p in ("node_modules", ".venv", "venv", "tests") for p in py_file.parts):
                    continue
                try:
                    for line in py_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                        m = re.match(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", line)
                        if m:
                            mod = m.group(1).lower()
                            # check if it's a known third-party library that's missing
                            known_libs = {"fastapi", "uvicorn", "pydantic", "httpx", "requests", "flask", "django", "sqlalchemy", "jwt", "dotenv"}
                            if mod in known_libs and mod not in req_pkgs:
                                missing_imports.add(mod)
                except Exception:
                    pass

            if missing_imports:
                findings.append(DriftFinding(
                    id="DRIFT-007",
                    title="Undeclared Python Dependencies in requirements.txt",
                    severity="CRITICAL",
                    category="MISSING_DEPENDENCY",
                    affected_files=["requirements.txt"],
                    explanation=f"Python code imports packages ({', '.join(missing_imports)}) that are not declared in requirements.txt. Setup will fail on clean machines.",
                    evidence=f"Code imports: {list(missing_imports)} | Manifest: {list(req_pkgs)}",
                    suggested_fix=f"Add missing packages to requirements.txt:\n" + "\n".join(missing_imports),
                ))

        return findings

