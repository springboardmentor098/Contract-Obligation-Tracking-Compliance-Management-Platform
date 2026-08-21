import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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

    # ============================================================
    # CONTRACT RELATIONSHIPS
    # ============================================================

    # Contracts created/owned by this user
    contracts = relationship(
        "Contract",
        foreign_keys="Contract.created_by",
        back_populates="owner",
    )

    # Contracts assigned to this user
    assigned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.assigned_to",
        back_populates="assignee",
    )

    # ============================================================
    # OTHER RELATIONSHIPS
    # ============================================================

    contract_versions = relationship(
        "ContractVersion",
        back_populates="creator",
    )

    obligations = relationship(
        "Obligation",
        back_populates="assignee",
    )

    renewals = relationship(
        "Renewal",
        back_populates="initiator",
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
    )

    reports = relationship(
        "Report",
        back_populates="generator",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
    )

    activities = relationship(
        "Activity",
        back_populates="user",
    )