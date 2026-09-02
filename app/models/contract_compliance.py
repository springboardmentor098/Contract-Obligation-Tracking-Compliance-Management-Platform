from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Float,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class ContractCompliance(Base):
    __tablename__ = "compliance_records"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================================
    # CONTRACT REFERENCE
    # =========================================================

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # =========================================================
    # COMPLIANCE INFORMATION
    # =========================================================

    status = Column(
        String,
        nullable=False
    )

    compliance_score = Column(
        Float,
        nullable=False
    )

    risk_level = Column(
        String,
        nullable=False
    )

    notes = Column(
        Text,
        nullable=True
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    evaluated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

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

    # =========================================================
    # CONTRACT RELATIONSHIP
    # =========================================================

    contract = relationship(
        "Contract",
        back_populates="compliance_records"
    )