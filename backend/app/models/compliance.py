import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Compliance(Base):
    __tablename__ = "compliance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id"),
        nullable=False,
        index=True,
    )

    compliance_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_obligations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    completed_obligations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    pending_obligations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    overdue_obligations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    delayed_obligations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    compliance_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Compliant",
    )

    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Low",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    contract = relationship(
        "Contract",
        back_populates="compliance_records",
    )