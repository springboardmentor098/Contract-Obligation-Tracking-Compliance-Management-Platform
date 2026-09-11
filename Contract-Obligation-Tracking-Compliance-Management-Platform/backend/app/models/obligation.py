from datetime import datetime

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


class Obligation(Base):
    __tablename__ = "obligations"

    # ============================================================
    # Primary Key
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # Contract
    # Foreign Key → contracts.id
    # ============================================================

    contract_id = Column(
        Integer,
        ForeignKey(
            "contracts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ============================================================
    # Obligation Information
    # ============================================================

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    obligation_type = Column(
        String(100),
        nullable=False
    )

    # ============================================================
    # Due Date
    # ============================================================

    due_date = Column(
        Date,
        nullable=False
    )

    # ============================================================
    # Responsible User
    # Foreign Key → users.id
    # ============================================================

    assigned_to = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    # ============================================================
    # Status
    # ============================================================

    status = Column(
        String(50),
        nullable=False,
        default="Pending"
    )

    # ============================================================
    # Completion
    # ============================================================

    completion_date = Column(
        Date,
        nullable=True
    )

    # ============================================================
    # Timestamps
    # ============================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ============================================================
    # Contract Relationship
    # ============================================================

    contract = relationship(
        "Contract",
        back_populates="obligations"
    )

    # ============================================================
    # Assigned User Relationship
    # ============================================================

    assignee = relationship(
        "User",
        back_populates="assigned_obligations"
    )

    # ============================================================
    # Renewal Relationship
    # ============================================================

    renewals = relationship(
        "Renewal",
        back_populates="obligation"
    )

    # ============================================================
    # Notification Relationship
    # ============================================================

    notifications = relationship(
        "Notification",
        back_populates="obligation"
    )
