from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    # -----------------------------
    # User Columns
    # -----------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Password is stored only as a hash
    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # -----------------------------
    # Relationships
    # -----------------------------

    # One User → Many Contracts Created
    contracts = relationship(
        "Contract",
        foreign_keys="Contract.created_by",
        back_populates="owner"
    )

    # One User → Many Contracts Assigned
    assigned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.assigned_to",
        back_populates="assignee"
    )

    # One User → Many Obligations Assigned
    assigned_obligations = relationship(
        "Obligation",
        foreign_keys="Obligation.assigned_to",
        back_populates="assignee"
    )

    # One User → Many Notifications
    notifications = relationship(
        "Notification",
        back_populates="user"
    )

    # One User → Many Reports
    reports = relationship(
        "Report",
        back_populates="generated_by_user"
    )

    # One User → Many Audit Logs
    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    # One User → Many Activities
    activities = relationship(
        "Activity",
        back_populates="user"
    )
