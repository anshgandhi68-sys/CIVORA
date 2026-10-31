"""0001 Initial Schema for CIVORA Core.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-31 06:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Repositories
    op.create_table(
        "repositories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("default_branch", sa.String(length=100), nullable=False),
        sa.Column("github_repo_id", sa.Integer(), nullable=True),
        sa.Column("installation_id", sa.Integer(), nullable=True),
        sa.Column("autopilot_enabled", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("full_name"),
        sa.UniqueConstraint("github_repo_id"),
    )
    op.create_index(op.f("ix_repositories_owner"), "repositories", ["owner"], unique=False)
    op.create_index(op.f("ix_repositories_name"), "repositories", ["name"], unique=False)
    op.create_index(op.f("ix_repositories_full_name"), "repositories", ["full_name"], unique=False)
    op.create_index(op.f("ix_repositories_installation_id"), "repositories", ["installation_id"], unique=False)

    # Runs
    op.create_table(
        "runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("repo_id", sa.String(length=36), nullable=False),
        sa.Column("commit_sha", sa.String(length=40), nullable=False),
        sa.Column("base_ref", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("failure_category", sa.String(length=50), nullable=False),
        sa.Column("extracted_instructions_count", sa.Integer(), nullable=False),
        sa.Column("provenance_verified", sa.Boolean(), nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=True),
        sa.Column("pr_url", sa.String(length=500), nullable=True),
        sa.Column("repair_branch", sa.String(length=200), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_runs_repo_id"), "runs", ["repo_id"], unique=False)
    op.create_index(op.f("ix_runs_commit_sha"), "runs", ["commit_sha"], unique=False)
    op.create_index(op.f("ix_runs_status"), "runs", ["status"], unique=False)
    op.create_index(op.f("ix_runs_failure_category"), "runs", ["failure_category"], unique=False)

    # Execution Steps
    op.create_table(
        "execution_steps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("command", sa.Text(), nullable=False),
        sa.Column("command_hash", sa.String(length=64), nullable=False),
        sa.Column("working_dir", sa.String(length=500), nullable=False),
        sa.Column("exit_code", sa.Integer(), nullable=False),
        sa.Column("stdout_preview", sa.Text(), nullable=True),
        sa.Column("stderr_preview", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_execution_steps_run_id"), "execution_steps", ["run_id"], unique=False)
    op.create_index(op.f("ix_execution_steps_command_hash"), "execution_steps", ["command_hash"], unique=False)

    # Interventions
    op.create_table(
        "interventions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("step_id", sa.String(length=36), nullable=True),
        sa.Column("candidate_id", sa.String(length=100), nullable=False),
        sa.Column("failure_type", sa.String(length=100), nullable=False),
        sa.Column("suggested_command", sa.Text(), nullable=False),
        sa.Column("command_hash", sa.String(length=64), nullable=False),
        sa.Column("runtime_image_digest", sa.String(length=100), nullable=True),
        sa.Column("config_hash", sa.String(length=64), nullable=True),
        sa.Column("test_exit_code", sa.Integer(), nullable=False),
        sa.Column("is_proven", sa.Boolean(), nullable=False),
        sa.Column("evidence_hash", sa.String(length=64), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["step_id"], ["execution_steps.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interventions_run_id"), "interventions", ["run_id"], unique=False)
    op.create_index(op.f("ix_interventions_candidate_id"), "interventions", ["candidate_id"], unique=False)
    op.create_index(op.f("ix_interventions_command_hash"), "interventions", ["command_hash"], unique=False)

    # Provenance Audits
    op.create_table(
        "provenance_audits",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("target_file", sa.String(length=500), nullable=False),
        sa.Column("patch_sha256", sa.String(length=64), nullable=False),
        sa.Column("base_commit_sha", sa.String(length=40), nullable=False),
        sa.Column("intervention_id", sa.String(length=36), nullable=True),
        sa.Column("diff_lines_count", sa.Integer(), nullable=False),
        sa.Column("is_path_whitelisted", sa.Boolean(), nullable=False),
        sa.Column("is_hash_matching", sa.Boolean(), nullable=False),
        sa.Column("is_allowed", sa.Boolean(), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_provenance_audits_run_id"), "provenance_audits", ["run_id"], unique=False)
    op.create_index(op.f("ix_provenance_audits_patch_sha256"), "provenance_audits", ["patch_sha256"], unique=False)

    # Evidence Artifacts
    op.create_table(
        "evidence_artifacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("artifact_type", sa.String(length=50), nullable=False),
        sa.Column("storage_uri", sa.String(length=1000), nullable=False),
        sa.Column("sha256_digest", sa.String(length=64), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evidence_artifacts_run_id"), "evidence_artifacts", ["run_id"], unique=False)
    op.create_index(op.f("ix_evidence_artifacts_artifact_type"), "evidence_artifacts", ["artifact_type"], unique=False)
    op.create_index(op.f("ix_evidence_artifacts_sha256_digest"), "evidence_artifacts", ["sha256_digest"], unique=False)


def downgrade() -> None:
    op.drop_table("evidence_artifacts")
    op.drop_table("provenance_audits")
    op.drop_table("interventions")
    op.drop_table("execution_steps")
    op.drop_table("runs")
    op.drop_table("repositories")

