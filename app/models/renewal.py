from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    renewal_id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.contract_id", ondelete="CASCADE"), nullable=False)
    renewal_type = Column(String(20), nullable=False)
    notice_period_days = Column(Integer, nullable=True)
    renewal_date = Column(Date, nullable=True)
    new_end_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=False)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
