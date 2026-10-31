"""Unit tests for Repository Intelligence and Drift Detection."""

import pytest
from pathlib import Path
from intelligence import RepoScanner, DriftDetector, DiagnosticsEngine


def test_repo_scanner_and_drift_detector(tmp_path):
    repo = tmp_path / "sample_app"
    repo.mkdir()

    # Create README with npm install, but repo has pnpm-lock.yaml
    (repo / "README.md").write_text("# Sample App\n\nRun:\n```bash\nnpm install\nnpm run build\n```\n")
    (repo / "pnpm-lock.yaml").write_text("lockfileVersion: 5.4\n")
    (repo / "package.json").write_text('{"name": "sample", "scripts": {"dev": "vite"}}\n')

    scanner = RepoScanner(str(repo))
    summary = scanner.scan()
    assert summary.repo_name == "sample_app"
    assert summary.has_readme

    detector = DriftDetector(str(repo))
    findings = detector.analyze(summary)

    # Should detect: 1) pnpm vs npm lockfile drift, 2) missing build script in package.json
    finding_cats = [f.category for f in findings]
    assert "OUTDATED_INSTALL" in finding_cats
    assert "BUILD_MISMATCH" in finding_cats


def test_diagnostics_engine():
    diag = DiagnosticsEngine()
    res = diag.diagnose(
        stderr="ModuleNotFoundError: No module named 'jwt'",
        stdout=""
    )
    assert res.category == "MISSING_DEPENDENCY"
    assert res.culprit == "jwt"
    assert "jwt" in res.suggested_action
