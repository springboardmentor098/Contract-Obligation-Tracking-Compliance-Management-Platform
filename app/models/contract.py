from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================================
    # CONTRACT INFORMATION
    # =========================================================

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

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=True
    )

    # =========================================================
    # CONTRACT WORKFLOW STATUS
    # =========================================================

    status = Column(
        String(50),
        nullable=False,
        default="Draft"
    )

    # =========================================================
    # CONTRACT CREATOR / OWNER
    # =========================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # =========================================================
    # CONTRACT ASSIGNMENT
    # =========================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # =========================================================
    # WORKFLOW TIMESTAMPS
    # =========================================================

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

    # =========================================================
    # RECORD TIMESTAMPS
    # =========================================================

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # =========================================================
    # USER RELATIONSHIPS
    # =========================================================

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_contracts"
    )

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_contracts"
    )

    # =========================================================
    # CONTRACT RELATIONSHIPS
    # =========================================================

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

    activities = relationship(
        "Activity",
        back_populates="contract"
    )

    # =========================================================
    # SPRINT 11 - COMPLIANCE RELATIONSHIP
    # =========================================================

    compliance_records = relationship(
        "ContractCompliance",
        back_populates="contract",
        cascade="all, delete-orphan"
    )