from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True,
        index=True
    )

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=True,
        index=True
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
        String(20),
        nullable=False,
        default="Unread",
        index=True
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
        nullable=False
    )

    updated_at = Column(
        DateTime,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="notifications"
    )

    contract = relationship(
        "Contract",
        back_populates="notifications"
    )

    obligation = relationship(
        "Obligation",
        back_populates="notifications"
    )
