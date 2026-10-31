"""Zero-Trust Provenance Audit SQLAlchemy Model."""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.run import Run


class ProvenanceAudit(Base, TimestampMixin):
    """Zero-Trust cryptographic audit record of documentation patch proposals."""

    __tablename__ = "provenance_audits"

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
    target_file: Mapped[str] = mapped_column(String(500), nullable=False)
    patch_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    base_commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    intervention_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    diff_lines_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_path_whitelisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hash_matching: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="provenance_audits")

    def __repr__(self) -> str:
        return f"<ProvenanceAudit(id='{self.id}', file='{self.target_file}', is_allowed={self.is_allowed})>"

