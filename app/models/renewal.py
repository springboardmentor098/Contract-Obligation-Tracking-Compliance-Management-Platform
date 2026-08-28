from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================================
    # CONTRACT
    # =========================================================

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False,
        index=True
    )

    # =========================================================
    # RENEWAL DATES
    # =========================================================

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

    # =========================================================
    # STATUS
    # =========================================================

    status = Column(
        String(50),
        nullable=False,
        default="Upcoming"
    )

    # =========================================================
    # ASSIGNED USER
    # =========================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # =========================================================
    # NOTES
    # =========================================================

    notes = Column(
        Text,
        nullable=True
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
    # CONTRACT RELATIONSHIP
    # =========================================================

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    # =========================================================
    # USER RELATIONSHIP
    # =========================================================

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_renewals"
    )