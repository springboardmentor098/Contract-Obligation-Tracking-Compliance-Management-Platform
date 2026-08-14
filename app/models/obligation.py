from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    obligation_id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.contract_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    obligation_type = Column(String(50), nullable=False)
    due_date = Column(Date, nullable=True)
    responsible_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(30), nullable=False)
    priority = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
