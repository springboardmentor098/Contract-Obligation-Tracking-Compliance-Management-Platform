from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
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

    notification_type = Column(
        String(50),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    channel = Column(
        String(30),
        nullable=False
    )

    is_read = Column(
        Boolean,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="notifications"
    )