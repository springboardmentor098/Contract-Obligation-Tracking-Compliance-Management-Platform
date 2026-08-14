from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(150), nullable=False)
    report_type = Column(String(50), nullable=False)
    generated_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    filters_json = Column(JSON, nullable=True)
    file_url = Column(String(500), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
