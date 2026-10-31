"""Execution Step SQLAlchemy Model."""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.run import Run
    from app.models.intervention import Intervention


class ExecutionStep(Base, TimestampMixin):
    """An individual setup command executed inside the isolated sandbox."""

    __tablename__ = "execution_steps"

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
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    command_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    working_dir: Mapped[str] = mapped_column(String(500), default="/workspace", nullable=False)
    
    exit_code: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)
    stdout_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stderr_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="steps")
    interventions: Mapped[list["Intervention"]] = relationship(
        "Intervention",
        back_populates="step",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ExecutionStep(id='{self.id}', index={self.step_index}, exit_code={self.exit_code})>"

