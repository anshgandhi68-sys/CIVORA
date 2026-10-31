"""Continuous Integration Inspection Tools (Read-Only)."""

from typing import Any, Dict, List, Optional
from app.mcp.github import GitHubAppClient, GitHubAppError
from app.mcp.tools.repository import repo_get_metadata


async def ci_get_workflows(
    owner: str,
    repo: str,
    client: Optional[GitHubAppClient] = None,
) -> Dict[str, Any]:
    """Retrieves all registered GitHub Actions workflows for the repository."""
    gh = client or GitHubAppClient()
    try:
        data = await gh.request("GET", f"repos/{owner}/{repo}/actions/workflows", owner, repo)

        workflows: List[Dict[str, Any]] = []
        for wf in data.get("workflows", []):
            workflows.append({
                "id": wf.get("id"),
                "name": wf.get("name"),
                "path": wf.get("path"),
                "state": wf.get("state"),
                "url": wf.get("html_url"),
            })

        return {
            "total_count": data.get("total_count", len(workflows)),
            "workflows": workflows,
        }
    except GitHubAppError as exc:
        return exc.to_dict()


async def ci_get_check_runs(
    owner: str,
    repo: str,
    ref: Optional[str] = None,
    client: Optional[GitHubAppClient] = None,
) -> Dict[str, Any]:
    """Retrieves all check runs for a specific commit reference, with explicit conclusion statuses."""
    gh = client or GitHubAppClient()
    try:
        resolved_ref = ref
        if not resolved_ref:
            meta = await repo_get_metadata(owner, repo, client=gh)
            if "error" in meta:
                return meta
            resolved_ref = meta.get("default_branch_head_sha", "main")

        data = await gh.request(
            "GET",
            f"repos/{owner}/{repo}/commits/{resolved_ref}/check-runs",
            owner,
            repo,
        )

        check_runs: List[Dict[str, Any]] = []
        for cr in data.get("check_runs", []):
            status = cr.get("status")
            conclusion = cr.get("conclusion")

            # Mark pending if check run is queued or in_progress without conclusion
            if not conclusion and status in ["queued", "in_progress", "waiting", "requested"]:
                conclusion = "pending"

            check_runs.append({
                "id": cr.get("id"),
                "name": cr.get("name"),
                "status": status,
                "conclusion": conclusion,
                "started_at": cr.get("started_at"),
                "completed_at": cr.get("completed_at"),
                "details_url": cr.get("html_url") or cr.get("details_url"),
            })

        return {
            "resolved_ref": resolved_ref,
            "total_count": data.get("total_count", len(check_runs)),
            "check_runs": check_runs,
        }
    except GitHubAppError as exc:
        return exc.to_dict()
