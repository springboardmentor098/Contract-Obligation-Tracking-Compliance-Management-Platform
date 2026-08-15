from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    contract_number = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )

    description = Column(Text, nullable=True)

    party_name = Column(String(255), nullable=True)

    start_date = Column(Date, nullable=True)

    end_date = Column(Date, nullable=True)

    status = Column(String(50), nullable=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # -------------------- USER --------------------

    owner = relationship(
        "User",
        back_populates="contracts"
    )

    # -------------------- CONTRACT VERSIONS --------------------

    versions = relationship(
        "ContractVersion",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # -------------------- OBLIGATIONS --------------------

    obligations = relationship(
        "Obligation",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # -------------------- RENEWALS --------------------

    renewals = relationship(
        "Renewal",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # -------------------- NOTIFICATIONS --------------------

    notifications = relationship(
        "Notification",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # -------------------- REPORTS --------------------

    reports = relationship(
        "Report",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # -------------------- AUDIT LOGS --------------------

    audit_logs = relationship(
        "AuditLog",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    # -------------------- ACTIVITIES --------------------

    activities = relationship(
        "Activity",
        back_populates="contract",
        cascade="all, delete-orphan"
    )