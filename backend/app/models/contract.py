from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        String(1000),
        nullable=True
    )

    start_date = Column(Date)
    end_date = Column(Date)

    status = Column(
        String(50),
        nullable=False,
        default="Draft"
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

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

    # Owner of the contract
    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="owned_contracts"
    )

    # User assigned to the contract
    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_contracts"
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
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    reports = relationship(
        "Report",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    activities = relationship(
        "Activity",
        back_populates="contract",
        cascade="all, delete-orphan"
    )
    compliance_records = relationship(
    "Compliance",
    back_populates="contract",
    cascade="all, delete-orphan"
    )
