from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base


class Compliance(Base):

    __tablename__ = "compliances"

    id = Column(Integer, primary_key=True, index=True)

    # Existing relationship
    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=True
    )

    # Sprint 11 contract-level compliance
    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True
    )

    status = Column(
        String,
        nullable=False
    )

    compliance_score = Column(
        Float,
        nullable=True
    )

    risk_level = Column(
        String,
        nullable=True
    )

    evaluated_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    notes = Column(
        Text,
        nullable=True
    )

    proof = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    contract = relationship(
        "Contract",
        back_populates="compliance_records"
    )

    obligation = relationship(
        "Obligation",
        back_populates="compliance_records"
    )