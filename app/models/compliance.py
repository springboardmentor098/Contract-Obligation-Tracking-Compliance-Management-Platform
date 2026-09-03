import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "Compliant"
    PENDING = "Pending"
    DELAYED = "Delayed"
    NON_COMPLIANT = "Non-Compliant"
    HIGH_RISK = "High Risk"


class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ComplianceRecord(Base):
    """
    Historical snapshot of a contract's compliance evaluation. Current live
    compliance is calculated on demand by ComplianceService; a row is written
    here each time an evaluation is (re)run, so compliance history is kept
    for audit/reporting purposes (Sprint 11, section 11).
    """

    __tablename__ = "compliance_records"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    status = Column(Enum(ComplianceStatus), nullable=False)
    compliance_score = Column(Float, nullable=False, default=0)
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.LOW)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contract = relationship("Contract")
