from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, synonym

from app.database.database import Base


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    compliance_status = Column(String(50), nullable=False, default="Compliant")
    compliance_score = Column(Float, nullable=False, default=100.0)
    risk_level = Column(String(50), nullable=False, default="Low")
    total_obligations = Column(Integer, nullable=False, default=0)
    completed_obligations = Column(Integer, nullable=False, default=0)
    pending_obligations = Column(Integer, nullable=False, default=0)
    overdue_obligations = Column(Integer, nullable=False, default=0)
    delayed_obligations = Column(Integer, nullable=False, default=0)
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Synonyms for backward compatibility
    compliance_id = synonym("id")
    status = synonym("compliance_status")

    # SQLAlchemy Relationship
    contract = relationship("Contract", back_populates="compliance_records")
