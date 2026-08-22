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


class Contract(Base):
    __tablename__ = "contracts"

    # ============================================================
    # Primary Key
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # Contract Information
    # ============================================================

    title = Column(
        String(200),
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
    # Contract Dates
    # ============================================================

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
    )

    # ============================================================
    # Contract Workflow Status
    # ============================================================

    status = Column(
        String(50),
        nullable=False,
        default="Draft"
    )

    # ============================================================
    # Contract Creator
    # ============================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ============================================================
    # Assigned Responsible User
    # ============================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    # ============================================================
    # Workflow Timestamps
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
    # General Timestamps
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
    # Creator Relationship
    # ============================================================

    owner = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="contracts"
    )

    # ============================================================
    # Assigned User Relationship
    # ============================================================

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_contracts"
    )

    # ============================================================
    # Contract Versions
    # ============================================================

    versions = relationship(
        "ContractVersion",
        back_populates="contract"
    )

    # ============================================================
    # Obligations
    # One Contract → Many Obligations
    # ============================================================

    obligations = relationship(
        "Obligation",
        back_populates="contract",
        cascade="all, delete-orphan"
    )
