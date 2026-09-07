from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        nullable=False
    )

    report_type = Column(
        String(100),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    generated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=True
    )

    generated_at = Column(
        DateTime,
        nullable=True
    )

    generated_by_user = relationship(
        "User",
        back_populates="reports"
    )
