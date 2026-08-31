from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="SET NULL"),
        nullable=True
    )

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id", ondelete="SET NULL"),
        nullable=True
    )

    notification_type = Column(String(100), nullable=False)

    title = Column(String(255), nullable=False)

    message = Column(Text, nullable=False)

    status = Column(String(20), default="Unread")

    scheduled_at = Column(DateTime(timezone=True), nullable=True)

    sent_at = Column(DateTime(timezone=True), nullable=True)

    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="notifications",
        passive_deletes=True
    )

    contract = relationship(
        "Contract",
        back_populates="notifications"
    )

    obligation = relationship(
        "Obligation",
        back_populates="notifications"
    )