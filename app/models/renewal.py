from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)

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
        String(30),
        nullable=False,
        default="Upcoming"
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    assigned_user = relationship(
        "User",
        back_populates="renewals"
    )
