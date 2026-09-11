from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
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
        index=True,
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
        String(20),
        nullable=False,
        default="Unread",
        index=True,
    )

    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    read_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
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
