from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    report_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)

    generated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="reports"
    )

    contract = relationship(
        "Contract",
        back_populates="reports"
    )