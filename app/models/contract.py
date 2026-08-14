from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    contract_number = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    category = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="Draft"
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # User who created the contract
    owner = relationship(
        "User",
        back_populates="contracts"
    )

    versions = relationship(
        "ContractVersion",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    obligations = relationship(
        "Obligation",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    renewals = relationship(
        "Renewal",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="contract"
    )

    reports = relationship(
        "Report",
        back_populates="contract"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="contract"
    )

    activities = relationship(
        "Activity",
        back_populates="contract"
    )