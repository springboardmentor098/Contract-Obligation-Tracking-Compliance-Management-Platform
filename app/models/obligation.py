from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    obligation_type = Column(
        String(100),
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="Pending"
    )

    completion_date = Column(
        Date,
        nullable=True
    )

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

    # Contract associated with this obligation
    contract = relationship(
        "Contract",
        back_populates="obligations"
    )

    # User responsible for this obligation
    assignee = relationship(
        "User",
        back_populates="obligations"
    )

    # Existing Activity relationship
    activities = relationship(
        "Activity",
        back_populates="obligation"
    )
    