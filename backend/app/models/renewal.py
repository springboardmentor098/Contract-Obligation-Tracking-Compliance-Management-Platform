from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    renewal_date = Column(
        Date,
        nullable=True
    )

    previous_expiry_date = Column(
        Date,
        nullable=False
    )

    new_expiry_date = Column(
        Date,
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="Upcoming"
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    notes = Column(
        String(1000),
        nullable=True
    )

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

    # Contract associated with this renewal
    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    # User responsible for this renewal
    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_renewals"
    )