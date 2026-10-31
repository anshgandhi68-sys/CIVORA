"""Evidence Artifact SQLAlchemy Model."""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.run import Run


class EvidenceArtifact(Base, TimestampMixin):
    """Immutable evidence artifact supporting audit trail and verifiable PRs."""

    __tablename__ = "evidence_artifacts"

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
    artifact_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # e.g., 'LOG_CONDENSED', 'DIFF_PATCH', 'INTERVENTION_PROOF', 'DEVCONTAINER_JSON'
    storage_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    sha256_digest: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    byte_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="evidence_artifacts")

    def __repr__(self) -> str:
        return f"<EvidenceArtifact(id='{self.id}', type='{self.artifact_type}', sha256='{self.sha256_digest[:8]}...')>"

