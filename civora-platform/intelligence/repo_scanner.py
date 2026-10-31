"""CIVORA Deep Repository Scanner.

Inspects directory structure, detects languages, frameworks, manifests,
environment configurations, CI pipelines, and README instructions.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from sandbox.security import validate_safe_path


LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".cpp": "C++",
    ".sh": "Shell",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
}

FRAMEWORK_SIGNATURES = {
    "FastAPI": ["fastapi", "uvicorn"],
    "Flask": ["flask"],
    "Django": ["django"],
    "React": ["react", "react-dom"],
    "Next.js": ["next"],
    "Vue.js": ["vue"],
    "Express": ["express"],
    "NestJS": ["@nestjs/core"],
    "Vite": ["vite"],
    "TailwindCSS": ["tailwindcss"],
    "PyTorch": ["torch"],
    "TensorFlow": ["tensorflow"],
}


@dataclass
class RepoIntelligenceSummary:
    repo_name: str
    root_path: str
    total_files: int
    languages: Dict[str, int]
    primary_language: str
    frameworks: List[str]
    manifests: Dict[str, Any]
    readme_content: Optional[str] = None
    readme_instructions: Dict[str, List[str]] = field(default_factory=dict)
    env_variables_detected: List[str] = field(default_factory=list)
    ci_workflows: List[str] = field(default_factory=list)
    docker_files: List[str] = field(default_factory=list)
    build_scripts: Dict[str, str] = field(default_factory=dict)

    @property
    def has_readme(self) -> bool:
        return bool(self.readme_content)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_name": self.repo_name,
            "root_path": self.root_path,
            "total_files": self.total_files,
            "languages": self.languages,
            "primary_language": self.primary_language,
            "frameworks": self.frameworks,
            "manifests": self.manifests,
            "has_readme": bool(self.readme_content),
            "readme_instructions": self.readme_instructions,
            "env_variables_detected": self.env_variables_detected,
            "ci_workflows": self.ci_workflows,
            "docker_files": self.docker_files,
            "build_scripts": self.build_scripts,
        }


class RepoScanner:
    """Scans repository workspaces to extract architecture, dependencies, and instructions."""

    def __init__(self, workspace_path: str):
        self.root = Path(workspace_path).resolve()

    def scan(self) -> RepoIntelligenceSummary:
        total_files = 0
        lang_counts: Dict[str, int] = {}
        frameworks_found: Set[str] = set()
        manifests: Dict[str, Any] = {}
        readme_content = None
        ci_workflows: List[str] = []
        docker_files: List[str] = []
        build_scripts: Dict[str, str] = {}
        code_env_vars: Set[str] = set()

        # Traverse workspace safely
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", ".venv", "venv", "__pycache__", "dist", "build")]
            for f in files:
                if f.startswith("."):
                    continue
                file_path = Path(root) / f
                rel_path = file_path.relative_to(self.root)
                total_files += 1

                ext = file_path.suffix.lower()
                if ext in LANGUAGE_EXTENSIONS:
                    lang = LANGUAGE_EXTENSIONS[ext]
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

                # Check for env var usages in code
                if ext in (".py", ".js", ".ts", ".jsx", ".tsx"):
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        # Python: os.getenv('XYZ'), os.environ.get('XYZ'), os.environ['XYZ']
                        py_vars = re.findall(r"os\.(?:getenv|environ(?:\[|\.get\())\s*['\"]([A-Z0-9_]{3,})['\"]", content)
                        code_env_vars.update(py_vars)
                        # JS/TS: process.env.XYZ
                        js_vars = re.findall(r"process\.env\.([A-Z0-9_]{3,})", content)
                        code_env_vars.update(js_vars)
                    except Exception:
                        pass

        # Parse Readme
        for readme_name in ("README.md", "README", "readme.md", "Readme.md"):
            r_path = self.root / readme_name
            if r_path.exists():
                try:
                    readme_content = r_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    pass
                break

        readme_instructions = self._extract_readme_instructions(readme_content or "")

        # Parse package.json
        pkg_json = self.root / "package.json"
        if pkg_json.exists():
            try:
                pkg_data = json.loads(pkg_json.read_text(encoding="utf-8", errors="ignore"))
                manifests["package.json"] = pkg_data
                scripts = pkg_data.get("scripts", {})
                build_scripts.update(scripts)
                all_deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                for fw, sigs in FRAMEWORK_SIGNATURES.items():
                    if any(sig in all_deps for sig in sigs):
                        frameworks_found.add(fw)
            except Exception:
                pass

        # Parse requirements.txt
        req_txt = self.root / "requirements.txt"
        if req_txt.exists():
            try:
                lines = [l.strip() for l in req_txt.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
                manifests["requirements.txt"] = lines
                req_lower = " ".join(lines).lower()
                for fw, sigs in FRAMEWORK_SIGNATURES.items():
                    if any(sig in req_lower for sig in sigs):
                        frameworks_found.add(fw)
            except Exception:
                pass

        # Parse Dockerfiles and CI
        for path in self.root.rglob("*"):
            if any(p in ("node_modules", ".venv", ".git") for p in path.parts):
                continue
            rel = str(path.relative_to(self.root))
            if "dockerfile" in path.name.lower():
                docker_files.append(rel)
            elif ".github/workflows" in rel and (rel.endswith(".yml") or rel.endswith(".yaml")):
                ci_workflows.append(rel)

        # Primary language
        primary_lang = "Unknown"
        if lang_counts:
            primary_lang = max(lang_counts.items(), key=lambda x: x[1])[0]

        return RepoIntelligenceSummary(
            repo_name=self.root.name,
            root_path=str(self.root),
            total_files=total_files,
            languages=lang_counts,
            primary_language=primary_lang,
            frameworks=sorted(list(frameworks_found)),
            manifests=manifests,
            readme_content=readme_content,
            readme_instructions=readme_instructions,
            env_variables_detected=sorted(list(code_env_vars)),
            ci_workflows=ci_workflows,
            docker_files=docker_files,
            build_scripts=build_scripts,
        )

    def _extract_readme_instructions(self, readme_text: str) -> Dict[str, List[str]]:
        """Extract shell instructions and code blocks from README."""
        instructions: Dict[str, List[str]] = {
            "install": [],
            "build": [],
            "test": [],
            "run": [],
            "prerequisites": [],
        }
        if not readme_text:
            return instructions

        # Extract code blocks
        blocks = re.findall(r"```(?:bash|sh|shell)?\n(.*?)```", readme_text, re.DOTALL)
        for block in blocks:
            for line in block.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Strip leading $
                if line.startswith("$ "):
                    line = line[2:].strip()

                if any(x in line for x in ("npm install", "yarn add", "pip install", "pnpm install", "bundle install")):
                    instructions["install"].append(line)
                elif any(x in line for x in ("npm run build", "yarn build", "make build", "cargo build")):
                    instructions["build"].append(line)
                elif any(x in line for x in ("pytest", "npm test", "yarn test", "cargo test", "python -m unittest")):
                    instructions["test"].append(line)
                elif any(x in line for x in ("npm start", "node ", "python ", "python3 ", "uvicorn ")):
                    instructions["run"].append(line)

        # Extract prerequisite mentions (e.g. Node 18+, Python 3.10+)
        prereq_matches = re.findall(r"(node(?:js)?\s*(?:v|>=|>)?\s*\d+(?:\.\d+)?|python\s*(?:v|>=|>)?\s*\d+(?:\.\d+)?)", readme_text, re.IGNORECASE)
        instructions["prerequisites"] = list(set(prereq_matches))

        return instructions
