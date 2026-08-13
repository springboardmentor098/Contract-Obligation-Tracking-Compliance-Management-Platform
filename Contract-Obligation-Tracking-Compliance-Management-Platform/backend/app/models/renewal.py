from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)

    obligation_id = Column(Integer, ForeignKey("obligations.id"))

    renewal_date = Column(Date)
    renewal_status = Column(String(50), default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    obligation = relationship("Obligation", back_populates="renewals")