from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class Compliance(Base):
    __tablename__ = "compliance_records"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # CONTRACT
    # ============================================================

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False,
        index=True
    )

    # ============================================================
    # COMPLIANCE STATUS
    #
    # Compliant
    # Pending
    # Delayed
    # Non-Compliant
    # ============================================================

    status = Column(
        String(50),
        nullable=False
    )

    # ============================================================
    # COMPLIANCE SCORE
    # ============================================================

    compliance_score = Column(
        Float,
        nullable=False
    )

    # ============================================================
    # RISK LEVEL
    #
    # Low
    # Medium
    # High
    # ============================================================

    risk_level = Column(
        String(50),
        nullable=False
    )

    # ============================================================
    # EVALUATION TIMESTAMP
    # ============================================================

    evaluated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # ============================================================
    # NOTES
    # ============================================================

    notes = Column(
        Text,
        nullable=True
    )

    # ============================================================
    # SYSTEM TIMESTAMPS
    # ============================================================

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ============================================================
    # CONTRACT RELATIONSHIP
    # ============================================================

    contract = relationship(
        "Contract",
        back_populates="compliance_records"
    )