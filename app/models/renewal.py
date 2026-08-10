from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
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

    new_expiry_date = Column(Date, nullable=True)

    status = Column(String(50), nullable=False)

    notes = Column(Text, nullable=True)

    approved_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship with Contract
    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    # Relationship with User
    approver = relationship(
        "User",
        back_populates="approved_renewals"
    )