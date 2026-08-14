from sqlalchemy import Column, BigInteger, String, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    contract_id = Column(
        BigInteger,
        ForeignKey("contracts.id"),
        nullable=False
    )

    assigned_to = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    details = Column(
        Text,
        nullable=True
    )

    due_date = Column(
        Date,
        nullable=False
    )

    frequency = Column(
        String(50),
        nullable=True
    )

    priority = Column(
        String(30),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False
    )

    evidence_required = Column(
        Boolean,
        default=False,
        nullable=False
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    contract = relationship(
        "Contract",
        backref="obligations"
    )

    assignee = relationship(
        "User",
        backref="obligations"
    )