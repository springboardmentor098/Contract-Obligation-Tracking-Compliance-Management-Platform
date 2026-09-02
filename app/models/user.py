from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    # =========================================================
    # USER INFORMATION
    # =========================================================

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

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=func.now()
    )

    # =========================================================
    # CONTRACT RELATIONSHIPS
    # =========================================================

    # Contracts created by this user
    created_contracts = relationship(
        "Contract",
        foreign_keys="Contract.created_by",
        back_populates="creator"
    )

    # Contracts assigned to this user
    assigned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.assigned_to",
        back_populates="assigned_user"
    )

    # =========================================================
    # CONTRACT VERSION RELATIONSHIP
    # =========================================================

    contract_versions = relationship(
        "ContractVersion",
        back_populates="creator"
    )

    # =========================================================
    # OBLIGATION RELATIONSHIP
    # =========================================================

    obligations = relationship(
        "Obligation",
        back_populates="assignee"
    )

   # =========================================================
   # =========================================================
   # RENEWAL RELATIONSHIP
   # =========================================================

    assigned_renewals = relationship(
       "Renewal",
        foreign_keys="Renewal.assigned_to",
        back_populates="assigned_user"
    )
    # =========================================================
    # NOTIFICATION RELATIONSHIP
    # =========================================================

    notifications = relationship(
        "Notification",
        back_populates="user"
    )

    # =========================================================
    # REPORT RELATIONSHIP
    # =========================================================

    reports = relationship(
        "Report",
        back_populates="generator"
    )

    # =========================================================
    # AUDIT LOG RELATIONSHIP
    # =========================================================

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    # =========================================================
    # ACTIVITY RELATIONSHIP
    # =========================================================

    activities = relationship(
        "Activity",
        back_populates="user"
    )