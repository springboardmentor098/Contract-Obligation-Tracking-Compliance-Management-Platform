from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, synonym

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    obligation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    obligation_type = Column(String(100), nullable=False)
    due_date = Column(Date, nullable=True)
    responsible_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(50), nullable=False, default="Pending")
    completion_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Synonyms so both id/obligation_id and assigned_to/responsible_user_id work seamlessly
    id = synonym("obligation_id")
    assigned_to = synonym("responsible_user_id")

    contract = relationship("Contract", back_populates="obligations")
    assignee = relationship("User", foreign_keys=[responsible_user_id])
