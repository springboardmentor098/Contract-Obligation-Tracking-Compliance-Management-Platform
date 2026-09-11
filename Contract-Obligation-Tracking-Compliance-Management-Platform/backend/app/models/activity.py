from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    activity_type = Column(String(100))
    description = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activities")