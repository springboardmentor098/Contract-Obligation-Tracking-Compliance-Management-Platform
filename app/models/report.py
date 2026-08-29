from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    generated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    report_type = Column(String(100), nullable=False)

    report_data = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="reports"
    )

    generated_by_user = relationship(
        "User",
        back_populates="reports"
    )