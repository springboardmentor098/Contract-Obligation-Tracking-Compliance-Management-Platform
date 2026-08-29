from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    renewal_date = Column(Date, nullable=False)

    previous_expiry_date = Column(Date, nullable=False)

    new_expiry_date = Column(Date, nullable=False)

    renewal_status = Column(
        String(50),
        nullable=False,
        default="Upcoming"
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    assigned_user = relationship(
        "User",
        back_populates="renewals"
    )