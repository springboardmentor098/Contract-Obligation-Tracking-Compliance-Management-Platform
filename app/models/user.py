import enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    ADMINISTRATOR = "Administrator"
    LEGAL_MANAGER = "Legal Manager"
    COMPLIANCE_OFFICER = "Compliance Officer"
    CONTRACT_MANAGER = "Contract Manager"
    DEPARTMENT_HEAD = "Department Head"
    EMPLOYEE = "Employee"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships (1 user -> many of these)
    contracts_created = relationship(
        "Contract", back_populates="creator", foreign_keys="Contract.created_by"
    )
    contracts_assigned = relationship(
        "Contract", back_populates="assignee", foreign_keys="Contract.assigned_to"
    )
    obligations_assigned = relationship("Obligation", back_populates="assignee")
    renewals_assigned = relationship("Renewal", back_populates="assignee")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    activities = relationship("Activity", back_populates="user")
