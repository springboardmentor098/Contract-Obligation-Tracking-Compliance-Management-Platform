from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True
    )

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=True
    )

    notification_type = Column(
        String(100),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="Unread"
    )

    scheduled_at = Column(
        DateTime,
        nullable=True
    )

    sent_at = Column(
        DateTime,
        nullable=True
    )

    read_at = Column(
        DateTime,
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

    user = relationship(
        "User",
        back_populates="notifications"
    )

    contract = relationship(
        "Contract",
        back_populates="notifications"
    )

    obligation = relationship(
        "Obligation"
    )