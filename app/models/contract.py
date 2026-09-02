from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # BASIC CONTRACT INFORMATION
    # ============================================================

    title = Column(
        String(255),
        nullable=False
    )

    contract_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    # ============================================================
    # CONTRACT DATES
    # ============================================================

    start_date = Column(
        Date,
        nullable=True
    )

    end_date = Column(
        Date,
        nullable=True
    )

    # ============================================================
    # CONTRACT STATUS
    #
    # Draft
    # Under Review
    # Approved
    # Active
    # Expired
    # Terminated
    # ============================================================

    status = Column(
        String(50),
        nullable=False,
        default="Draft"
    )

    # ============================================================
    # CONTRACT CREATOR
    # ============================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ============================================================
    # CONTRACT ASSIGNMENT
    # ============================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # ============================================================
    # WORKFLOW TIMESTAMPS
    # ============================================================

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

    # ============================================================
    # SYSTEM TIMESTAMPS
    # ============================================================

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ============================================================
    # CREATOR RELATIONSHIP
    # ============================================================

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="contracts"
    )

    # ============================================================
    # ASSIGNED USER RELATIONSHIP
    # ============================================================

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_contracts"
    )

    # ============================================================
    # CONTRACT VERSIONS
    # ============================================================

    versions = relationship(
        "ContractVersion",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # OBLIGATIONS
    # ============================================================

    obligations = relationship(
        "Obligation",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # RENEWALS
    # ============================================================

    renewals = relationship(
        "Renewal",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # NOTIFICATIONS
    # ============================================================

    notifications = relationship(
        "Notification",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # REPORTS
    # ============================================================

    reports = relationship(
        "Report",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # AUDIT LOGS
    # ============================================================

    audit_logs = relationship(
        "AuditLog",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # ACTIVITIES
    # ============================================================

    activities = relationship(
        "Activity",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # COMPLIANCE RECORDS
    # ============================================================

    compliance_records = relationship(
        "Compliance",
        back_populates="contract",
        cascade="all, delete-orphan"
    )