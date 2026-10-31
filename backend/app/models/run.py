"""Execution Run SQLAlchemy Model and Enums."""

import enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.execution_step import ExecutionStep
    from app.models.intervention import Intervention
    from app.models.provenance import ProvenanceAudit
    from app.models.evidence import EvidenceArtifact


class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXTRACTING = "EXTRACTING"
    RUNNING_SANDBOX = "RUNNING_SANDBOX"
    DIAGNOSING = "DIAGNOSING"
    PROVING_FIX = "PROVING_FIX"
    VERIFYING_CLEAN = "VERIFYING_CLEAN"
    GENERATING_PR = "GENERATING_PR"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class FailureCategory(str, enum.Enum):
    NONE = "NONE"
    MISSING_ENV = "MISSING_ENV"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    LOCKFILE_MISMATCH = "LOCKFILE_MISMATCH"
    MISSING_EDITABLE_INSTALL = "MISSING_EDITABLE_INSTALL"
    MISSING_SYSTEM_DEP = "MISSING_SYSTEM_DEP"
    CODE_DEFECT = "CODE_DEFECT"
    SECURITY_BLOCKED = "SECURITY_BLOCKED"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class Run(Base, TimestampMixin):
    """A complete autonomous onboarding & repair run on a repository commit."""

    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    repo_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    base_ref: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus),
        default=RunStatus.PENDING,
        nullable=False,
        index=True,
    )
    failure_category: Mapped[FailureCategory] = mapped_column(
        Enum(FailureCategory),
        default=FailureCategory.NONE,
        nullable=False,
        index=True,
    )
    
    extracted_instructions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    provenance_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pr_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pr_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    repair_branch: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    finished_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository", back_populates="runs", lazy="selectin")
    steps: Mapped[List["ExecutionStep"]] = relationship(
        "ExecutionStep",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="ExecutionStep.step_index",
        lazy="selectin",
    )
    interventions: Mapped[List["Intervention"]] = relationship(
        "Intervention",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    provenance_audits: Mapped[List["ProvenanceAudit"]] = relationship(
        "ProvenanceAudit",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    evidence_artifacts: Mapped[List["EvidenceArtifact"]] = relationship(
        "EvidenceArtifact",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Run(id='{self.id}', repo_id='{self.repo_id}', status='{self.status}')>"
