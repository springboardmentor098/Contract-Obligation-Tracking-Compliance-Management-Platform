from datetime import datetime, timezone

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
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    obligation_type = Column(
        String,
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="Pending"
    )

    progress = Column(
        Integer,
        nullable=False,
        default=0
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    contract = relationship(
        "Contract",
        back_populates="obligations"
    )

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="obligations"
    )

    notifications = relationship(
        "Notification",
        back_populates="obligation"
    )