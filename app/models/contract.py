from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    contract_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    counterparty_name = Column(
        String(255),
        nullable=False,
    )

    start_date = Column(
        Date,
        nullable=False,
    )

    end_date = Column(
        Date,
        nullable=True,
    )

    # User who created the contract
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # User responsible for managing the contract
    assigned_to = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="Draft",
        index=True,
    )

    reviewed_at = Column(
        DateTime,
        nullable=True,
    )

    approved_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # -----------------------------
    # User relationships
    # -----------------------------

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_contracts",
    )

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_contracts",
    )

    # -----------------------------
    # Contract relationships
    # -----------------------------

    versions = relationship(
        "ContractVersion",
        back_populates="contract",
        cascade="all, delete-orphan",
    )

    obligations = relationship(
        "Obligation",
        back_populates="contract",
        cascade="all, delete-orphan",
    )

    renewals = relationship(
        "Renewal",
        back_populates="contract",
        cascade="all, delete-orphan",
    )

    notifications = relationship(
        "Notification",
        back_populates="contract",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "Report",
        back_populates="contract",
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="contract",
        cascade="all, delete-orphan",
    )

    activities = relationship(
        "Activity",
        back_populates="contract",
        cascade="all, delete-orphan",
    )