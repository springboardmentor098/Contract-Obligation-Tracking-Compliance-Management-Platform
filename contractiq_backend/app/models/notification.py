from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        BigInteger,
        ForeignKey("contracts.id"),
        nullable=False
    )

    obligation_id = Column(
        BigInteger,
        ForeignKey("obligations.id"),
        nullable=True
    )

    renewal_id = Column(
        BigInteger,
        ForeignKey("renewals.id"),
        nullable=True
    )

    notification_type = Column(
        String(50),
        nullable=False
    )

    subject = Column(
        String(200),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    sent_at = Column(
        DateTime,
        nullable=True
    )

    user = relationship(
        "User",
        backref="notifications"
    )

    contract = relationship(
        "Contract",
        backref="notifications"
    )

    obligation = relationship(
        "Obligation",
        backref="notifications"
    )

    renewal = relationship(
        "Renewal",
        backref="notifications"
    )