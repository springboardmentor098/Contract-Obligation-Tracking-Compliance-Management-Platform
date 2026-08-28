from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    activity = Column(String(500))

    user = relationship("User", back_populates="activities", passive_deletes=True)
    contract = relationship("Contract", back_populates="activities")