from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    # ============================================================
    # Primary Key
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # Contract Information
    # ============================================================

    title = Column(
        String(200),
        nullable=False
    )

    contract_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    # ============================================================
    # Contract Dates
    # ============================================================

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
    )

    # ============================================================
    # Contract Status
    # ============================================================

    # Every newly created contract starts as Draft.
    status = Column(
        String(50),
        nullable=False,
        default="Draft"
    )

    # ============================================================
    # Contract Creator
    # Foreign Key → users.id
    # ============================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ============================================================
    # Timestamps
    # ============================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ============================================================
    # User Relationship
    # One User → Many Contracts
    # ============================================================

    owner = relationship(
        "User",
        back_populates="contracts"
    )

    # ============================================================
    # Future Contract Relationships
    # ============================================================

    versions = relationship(
        "ContractVersion",
        back_populates="contract"
    )

    obligations = relationship(
        "Obligation",
        back_populates="contract"
    )
