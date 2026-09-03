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


class Obligation(Base):
    __tablename__ = "obligations"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # CONTRACT
    # ============================================================

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    # ============================================================
    # BASIC INFORMATION
    # ============================================================

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    # ============================================================
    # OBLIGATION TYPE
    #
    # Payment Obligation
    # Delivery Commitment
    # Reporting Requirement
    # Renewal Condition
    # Service Level Agreement
    # Legal Compliance Requirement
    # ============================================================

    obligation_type = Column(
        String(100),
        nullable=False
    )

    # ============================================================
    # DUE DATE
    # ============================================================

    due_date = Column(
        Date,
        nullable=False
    )

    # ============================================================
    # STATUS
    #
    # Pending
    # In Progress
    # Completed
    # Delayed
    # Overdue
    # ============================================================

    status = Column(
        String(50),
        nullable=False,
        default="Pending"
    )

    # ============================================================
    # PRIORITY
    # Existing project field - preserved
    # ============================================================

    priority = Column(
        String(50),
        nullable=True
    )

    # ============================================================
    # ASSIGNED USER
    # ============================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ============================================================
    # COMPLETION
    # ============================================================

    completion_date = Column(
        Date,
        nullable=True
    )

    # ============================================================
    # TIMESTAMPS
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
    # CONTRACT RELATIONSHIP
    # ============================================================

    contract = relationship(
        "Contract",
        back_populates="obligations"
    )

    # ============================================================
    # USER RELATIONSHIP
    # ============================================================

    assignee = relationship(
        "User",
        back_populates="obligations"
    )

    # ============================================================
    # NOTIFICATIONS
    # ============================================================

    notifications = relationship(
        "Notification",
        back_populates="obligation",
        cascade="all, delete-orphan"
    )