"""Repository SQLAlchemy Model."""

from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.run import Run


class Repository(Base, TimestampMixin):
    """Connected GitHub Repository record."""

    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    owner: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    github_repo_id: Mapped[int] = mapped_column(Integer, nullable=True, unique=True)
    installation_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    autopilot_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    runs: Mapped[List["Run"]] = relationship(
        "Run",
        back_populates="repository",
        cascade="all, delete-orphan",
        order_by="desc(Run.created_at)",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Repository(id='{self.id}', full_name='{self.full_name}', autopilot={self.autopilot_enabled})>"
