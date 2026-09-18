from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True)
    activity = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    user_name = Column(String(100), nullable=True)
    user_role = Column(String(50), nullable=True, index=True)
    action = Column(String(100), nullable=True, index=True)
    entity_type = Column(String(100), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    status = Column(String(50), default="Success", nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)

    user = relationship("User", back_populates="activities", passive_deletes=True)
    contract = relationship("Contract", back_populates="activities")