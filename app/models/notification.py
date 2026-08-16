from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    related_contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=True)
    related_obligation_id = Column(Integer, ForeignKey("obligations.obligation_id", ondelete="CASCADE"), nullable=True)
    type = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
