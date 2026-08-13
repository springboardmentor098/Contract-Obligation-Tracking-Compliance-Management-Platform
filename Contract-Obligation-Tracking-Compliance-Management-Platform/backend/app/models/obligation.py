from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(Integer, ForeignKey("contracts.id"))

    obligation_name = Column(String(200), nullable=False)
    description = Column(Text)

    due_date = Column(Date)
    status = Column(String(50), default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="obligations")

    renewals = relationship("Renewal", back_populates="obligation")
    notifications = relationship("Notification", back_populates="obligation")