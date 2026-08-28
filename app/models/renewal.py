from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, synonym

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    renewal_date = Column(Date, nullable=True)
    previous_expiry_date = Column(Date, nullable=True)
    new_expiry_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Upcoming")
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Synonym for backward compatibility
    renewal_id = synonym("id")

    # SQLAlchemy Relationships
    contract = relationship("Contract", back_populates="renewals")
    assignee = relationship("User", foreign_keys=[assigned_to])
