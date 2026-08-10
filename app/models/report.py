from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    report_type = Column(String(100), nullable=False)

    generated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    file_path = Column(String(500), nullable=True)

    format = Column(String(20), nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship with User
    generator = relationship(
        "User",
        back_populates="reports"
    )