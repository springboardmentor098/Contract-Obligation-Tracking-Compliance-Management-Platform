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

    password_hash = Column(
        String(255),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # ============================================================
    # RELATIONSHIP WITH CONTRACTS
    # ============================================================

    contracts = relationship(
        "Contract",
        back_populates="creator"
    )

    # ============================================================
    # RELATIONSHIP WITH CONTRACT VERSIONS
    # ============================================================

    created_versions = relationship(
        "ContractVersion",
        back_populates="creator"
    )

    # ============================================================
    # RELATIONSHIP WITH OBLIGATIONS
    # ============================================================

    obligations = relationship(
        "Obligation",
        back_populates="assignee"
    )

    # ============================================================
    # RELATIONSHIP WITH NOTIFICATIONS
    # ============================================================

    notifications = relationship(
        "Notification",
        back_populates="user"
    )

    # ============================================================
    # RELATIONSHIP WITH REPORTS
    # ============================================================

    reports = relationship(
        "Report",
        back_populates="generator"
    )

    # ============================================================
    # RELATIONSHIP WITH AUDIT LOGS
    # ============================================================

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    # ============================================================
    # RELATIONSHIP WITH ACTIVITIES
    # ============================================================

    activities = relationship(
        "Activity",
        back_populates="user"
    )