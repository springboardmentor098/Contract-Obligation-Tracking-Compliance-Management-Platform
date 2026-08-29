from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Contract associated with this renewal
    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Date on which renewal was processed
    renewal_date = Column(
        Date,
        nullable=True,
    )

    # Previous contract expiry date
    previous_expiry_date = Column(
        Date,
        nullable=False,
    )

    # New expiry date after successful renewal
    new_expiry_date = Column(
        Date,
        nullable=True,
    )

    # Upcoming / In Progress / Renewed / Expired / Cancelled
    status = Column(
        String(50),
        nullable=False,
        default="Upcoming",
        index=True,
    )

    # User responsible for renewal
    assigned_to = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Additional information
    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------
    # Relationships
    # --------------------------------------------------

    contract = relationship(
        "Contract",
        back_populates="renewals",
    )

    assigned_user = relationship(
        "User",
        back_populates="renewals",
        foreign_keys=[assigned_to],
    )
