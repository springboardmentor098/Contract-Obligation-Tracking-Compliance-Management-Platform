from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=False
    )

    type = Column(
        String(50),
        nullable=True
    )

    title = Column(
        String(255),
        nullable=True
    )

    message = Column(
        Text,
        nullable=True
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    scheduled_at = Column(
        DateTime,
        nullable=True
    )

    sent_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=True
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
