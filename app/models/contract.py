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

    # Contract workflow status
    status = Column(
        String,
        nullable=False,
        default="Draft"
    )

    # User who created the contract
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # User responsible for the contract
    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Workflow timestamps
    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Required timestamps
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
        foreign_keys=[created_by],
        back_populates="contracts"
    )

    # User responsible for the contract
    assignee = relationship(
        "User",
        foreign_keys=[assigned_to]
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