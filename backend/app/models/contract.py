import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    contract_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    counterparty_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Draft",
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    contract_value: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        CHAR(3),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # User who created/owns the contract
    owner = relationship(
        "User",
        back_populates="contracts",
        foreign_keys=[created_by],
    )

    # User to whom the contract is assigned
    assignee = relationship(
        "User",
        back_populates="assigned_contracts",
        foreign_keys=[assigned_to],
    )

    versions = relationship(
        "ContractVersion",
        back_populates="contract",
    )

    obligations = relationship(
        "Obligation",
        back_populates="contract",
    )

    renewals = relationship(
        "Renewal",
        back_populates="contract",
    )

    notifications = relationship(
        "Notification",
        back_populates="contract",
    )

    reports = relationship(
        "Report",
        back_populates="contract",
    )

    activities = relationship(
        "Activity",
        back_populates="contract",
    )