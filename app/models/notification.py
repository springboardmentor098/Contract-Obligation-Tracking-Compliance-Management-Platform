from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
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
        nullable=True
    )

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=True
    )

    notification_type = Column(String(100), nullable=False)

    message = Column(Text, nullable=False)

    channel = Column(String(50), nullable=False)

    is_read = Column(Boolean, nullable=False, default=False)

    sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship with User
    user = relationship(
        "User",
        back_populates="notifications"
    )

    # Relationship with Contract
    contract = relationship(
        "Contract",
        back_populates="notifications"
    )

    # Relationship with Obligation
    obligation = relationship(
        "Obligation",
        back_populates="notifications"
    )