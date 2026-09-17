from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    compliance_score = Column(
        Integer,
        nullable=False
    )

    risk_level = Column(
        String(50),
        nullable=False
    )

    evaluated_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="compliance_records"
    )