from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationship with Contracts
    contracts = relationship(
        "Contract",
        back_populates="owner"
    )

    # Relationship with Contract Versions
    contract_versions = relationship(
        "ContractVersion",
        back_populates="creator"
    )

    # Relationship with Obligations
    obligations = relationship(
        "Obligation",
        back_populates="assignee"
    )

    # Relationship with Renewals
    approved_renewals = relationship(
        "Renewal",
        back_populates="approver"
    )

    # Relationship with Notifications
    notifications = relationship(
        "Notification",
        back_populates="user"
    )

    # Relationship with Reports
    reports = relationship(
        "Report",
        back_populates="generator"
    )

    # Relationship with Audit Logs
    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    # Relationship with Activities
    activities = relationship(
        "Activity",
        back_populates="user"
    )