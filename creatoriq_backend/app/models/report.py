from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    report_type = Column(
        String(50),
        nullable=False
    )

    generated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    file_format = Column(
        String(20),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False
    )

    generator = relationship(
        "User",
        back_populates="generated_reports"
    )