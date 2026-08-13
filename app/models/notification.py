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

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True
    )

    title = Column(String(255), nullable=False)

    message = Column(Text, nullable=False)

    notification_type = Column(String(50), nullable=True)

    is_read = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, nullable=True)

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