from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    role = Column(String(50), nullable=False)

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # Relationship with Contracts
    contracts = relationship(
        "Contract",
        back_populates="owner"
    )

    # Relationship with Contract Versions
    created_versions = relationship(
        "ContractVersion",
        back_populates="creator"
    )

    # Relationship with Obligations
    obligations = relationship(
        "Obligation",
        back_populates="assignee"
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