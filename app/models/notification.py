from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, synonym

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=True)
    obligation_id = Column(Integer, ForeignKey("obligations.obligation_id", ondelete="CASCADE"), nullable=True)
    notification_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="Unread")
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Synonyms for backward compatibility
    notification_id = synonym("id")
    type = synonym("notification_type")

    # SQLAlchemy Relationships
    user = relationship("User", foreign_keys=[user_id])
    contract = relationship("Contract", foreign_keys=[contract_id])
    obligation = relationship("Obligation", foreign_keys=[obligation_id])
