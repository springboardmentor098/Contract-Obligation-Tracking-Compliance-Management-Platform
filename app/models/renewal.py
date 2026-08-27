from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # CONTRACT
    # ============================================================

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    # ============================================================
    # RENEWAL DATES
    # ============================================================

    renewal_date = Column(
        Date,
        nullable=False
    )

    previous_expiry_date = Column(
        Date,
        nullable=False
    )

    new_expiry_date = Column(
        Date,
        nullable=True
    )

    # ============================================================
    # STATUS
    # ============================================================

    status = Column(
        String(50),
        nullable=False,
        default="Upcoming"
    )

    # ============================================================
    # ASSIGNED USER
    # ============================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # ============================================================
    # ADDITIONAL INFORMATION
    # ============================================================

    notes = Column(
        Text,
        nullable=True
    )

    # ============================================================
    # TIMESTAMPS
    # ============================================================

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

    # ============================================================
    # CONTRACT RELATIONSHIP
    # ============================================================

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    # ============================================================
    # USER RELATIONSHIP
    # ============================================================

    assignee = relationship(
        "User",
        back_populates="renewals"
    )