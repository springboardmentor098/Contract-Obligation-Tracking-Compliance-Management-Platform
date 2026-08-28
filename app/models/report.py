from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    report_name = Column(String(255))
    report_type = Column(String(100))
    file_path = Column(String(255))

    user = relationship("User", back_populates="reports", passive_deletes=True)