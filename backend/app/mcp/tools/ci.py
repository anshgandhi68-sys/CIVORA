"""Continuous Integration Inspection Tools (Read-Only)."""

from typing import Any, Dict, List, Optional
from app.mcp.github import GitHubAppClient, GitHubAppError, MAX_WORKFLOWS_PAGE_SIZE, MAX_CHECK_RUNS_PAGE_SIZE
from app.mcp.tools.repository import repo_get_metadata


async def ci_get_workflows(
    owner: str,
    repo: str,
    client: Optional[GitHubAppClient] = None,
) -> Dict[str, Any]:
    """Retrieves all registered GitHub Actions workflows for the repository.

    Results are bounded to MAX_WORKFLOWS_PAGE_SIZE entries. Pagination beyond
    this limit is not performed — the caller is informed via the bounded_at field.
    """
    gh = client or GitHubAppClient()
    try:
        data = await gh.request(
            "GET",
            f"repos/{owner}/{repo}/actions/workflows",
            owner,
            repo,
            params={"per_page": MAX_WORKFLOWS_PAGE_SIZE, "page": 1},
        )

        all_workflows: List[Dict[str, Any]] = data.get("workflows", [])
        # Enforce safe upper bound
        bounded = all_workflows[:MAX_WORKFLOWS_PAGE_SIZE]

        workflows: List[Dict[str, Any]] = []
        for wf in bounded:
            workflows.append({
                "id": wf.get("id"),
                "name": wf.get("name"),
                "path": wf.get("path"),
                "state": wf.get("state"),
                "url": wf.get("html_url"),
            })

        total_count = data.get("total_count", len(workflows))
        return {
            "total_count": total_count,
            "returned_count": len(workflows),
            "bounded_at": MAX_WORKFLOWS_PAGE_SIZE,
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
    """Retrieves all check runs for a specific commit reference, with explicit conclusion statuses.

    Results are bounded to MAX_CHECK_RUNS_PAGE_SIZE entries. Pagination beyond
    this limit is not performed — the caller is informed via the bounded_at field.
    """
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
            params={"per_page": MAX_CHECK_RUNS_PAGE_SIZE, "page": 1},
        )

        all_check_runs: List[Dict[str, Any]] = data.get("check_runs", [])
        # Enforce safe upper bound
        bounded = all_check_runs[:MAX_CHECK_RUNS_PAGE_SIZE]

        check_runs: List[Dict[str, Any]] = []
        for cr in bounded:
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

        total_count = data.get("total_count", len(check_runs))
        return {
            "resolved_ref": resolved_ref,
            "total_count": total_count,
            "returned_count": len(check_runs),
            "bounded_at": MAX_CHECK_RUNS_PAGE_SIZE,
            "check_runs": check_runs,
        }
    except GitHubAppError as exc:
        return exc.to_dict()
