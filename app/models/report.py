from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    generated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    file_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, nullable=False)
    generator = relationship("User", back_populates="reports")