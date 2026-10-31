"""Intervention SQLAlchemy Model."""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.run import Run
    from app.models.execution_step import ExecutionStep


class Intervention(Base, TimestampMixin):
    """A counterfactual intervention candidate tested inside the sandbox."""

    __tablename__ = "interventions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("execution_steps.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    candidate_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    failure_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    suggested_command: Mapped[str] = mapped_column(Text, nullable=False)
    command_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    runtime_image_digest: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    config_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    test_exit_code: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)
    is_proven: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evidence_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    verified_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="interventions")
    step: Mapped[Optional["ExecutionStep"]] = relationship("ExecutionStep", back_populates="interventions")

    def __repr__(self) -> str:
        return f"<Intervention(id='{self.id}', candidate='{self.candidate_id}', is_proven={self.is_proven})>"

