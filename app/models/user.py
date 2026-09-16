from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class UserRole(str, Enum):
    ADMINISTRATOR = "Administrator"
    LEGAL_MANAGER = "Legal Manager"
    COMPLIANCE_OFFICER = "Compliance Officer"
    CONTRACT_MANAGER = "Contract Manager"
    DEPARTMENT_HEAD = "Department Head"
    EMPLOYEE = "Employee"


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    full_name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    role = Column(
        String(50),
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    hashed_password = Column(
        String(255),
        nullable=False,
    )

    # ---------------------------------
    # Contracts created by this user
    # ---------------------------------
    created_contracts = relationship(
        "Contract",
        foreign_keys="Contract.created_by",
        back_populates="creator",
    )

    # ---------------------------------
    # Contracts assigned to this user
    # ---------------------------------
    assigned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.assigned_to",
        back_populates="assignee",
    )

    # ---------------------------------
    # Other relationships
    # ---------------------------------
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "Report",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    activities = relationship(
        "Activity",
        back_populates="user",
        cascade="all, delete-orphan",
    )