"""Unit Tests for Database Models and Relationships."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository import Repository
from app.models.run import Run, RunStatus, FailureCategory
from app.models.execution_step import ExecutionStep
from app.models.intervention import Intervention
from app.models.provenance import ProvenanceAudit
from app.models.evidence import EvidenceArtifact


@pytest.mark.asyncio
async def test_create_repository(db_session: AsyncSession):
    """Verify repository creation and query."""
    repo = Repository(
        owner="anshgandhi68-sys",
        name="CIVORA",
        full_name="anshgandhi68-sys/CIVORA",
        default_branch="main",
        autopilot_enabled=True,
    )
    db_session.add(repo)
    await db_session.flush()

    assert repo.id is not None
    assert len(repo.id) == 36
    assert repo.created_at is not None

    stmt = select(Repository).where(Repository.full_name == "anshgandhi68-sys/CIVORA")
    result = await db_session.execute(stmt)
    saved_repo = result.scalar_one_or_none()
    assert saved_repo is not None
    assert saved_repo.name == "CIVORA"
    assert saved_repo.autopilot_enabled is True


@pytest.mark.asyncio
async def test_create_run_and_relationships(db_session: AsyncSession):
    """Verify run creation with steps, interventions, provenance audit and evidence."""
    repo = Repository(
        owner="civora-evals",
        name="pulse-api",
        full_name="civora-evals/pulse-api",
    )
    db_session.add(repo)
    await db_session.flush()

    run = Run(
        repo_id=repo.id,
        commit_sha="a44764a51e60f25603c734064a37651c6c543210",
        base_ref="main",
        status=RunStatus.RUNNING_SANDBOX,
        failure_category=FailureCategory.MISSING_ENV,
    )
    db_session.add(run)
    await db_session.flush()

    # Add execution step
    step = ExecutionStep(
        run_id=run.id,
        step_index=1,
        command="npm install",
        command_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        exit_code=0,
        duration_ms=450,
        is_verified=True,
    )
    db_session.add(step)
    await db_session.flush()

    # Add intervention
    intervention = Intervention(
        run_id=run.id,
        step_id=step.id,
        candidate_id="MISSING_ENV_EXAMPLE_COPY",
        failure_type="MISSING_ENV",
        suggested_command="cp .env.example .env",
        command_hash="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
        test_exit_code=0,
        is_proven=True,
    )
    db_session.add(intervention)

    # Add provenance audit
    audit = ProvenanceAudit(
        run_id=run.id,
        target_file="README.md",
        patch_sha256="b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
        base_commit_sha=run.commit_sha,
        diff_lines_count=4,
        is_path_whitelisted=True,
        is_hash_matching=True,
        is_allowed=True,
    )
    db_session.add(audit)

    # Add evidence artifact
    evidence = EvidenceArtifact(
        run_id=run.id,
        artifact_type="DIFF_PATCH",
        storage_uri="evidence/runs/pulse-api/diff.patch",
        sha256_digest="b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
        byte_size=240,
    )
    db_session.add(evidence)
    await db_session.flush()

    # Query back
    stmt = select(Run).where(Run.id == run.id)
    result = await db_session.execute(stmt)
    saved_run = result.scalar_one()

    assert saved_run.status == RunStatus.RUNNING_SANDBOX
    assert saved_run.failure_category == FailureCategory.MISSING_ENV
    assert len(saved_run.steps) == 1
    assert len(saved_run.interventions) == 1
    assert len(saved_run.provenance_audits) == 1
    assert len(saved_run.evidence_artifacts) == 1

