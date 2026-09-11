from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    report_name = Column(String(200), nullable=False)
    report_type = Column(String(100))

    generated_by = Column(Integer, ForeignKey("users.id"))

    file_path = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)

    generated_by_user = relationship("User", back_populates="reports")
