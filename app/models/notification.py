from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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

    message = Column(Text, nullable=False)

    notification_type = Column(String(50), nullable=False)

    is_read = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),
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