from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    notification_type = Column(
        String(100),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="Unread",
    )

    scheduled_at = Column(
        DateTime,
        nullable=True,
    )

    sent_at = Column(
        DateTime,
        nullable=True,
    )

    read_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="notifications",
    )

    contract = relationship(
        "Contract",
        back_populates="notifications",
    )

    obligation = relationship(
        "Obligation",
        back_populates="notifications",
    )