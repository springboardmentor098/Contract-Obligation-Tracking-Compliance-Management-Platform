from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
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

    status = Column(String(50), nullable=False, default="Upcoming")

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    notes = Column(String, nullable=True)

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

    contract = relationship("Contract")

    assigned_user = relationship("User")