# app/models/notification.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =========================================================
    # USER
    # =========================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    # =========================================================
    # CONTRACT
    # =========================================================

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True,
    )

    # =========================================================
    # OBLIGATION
    # =========================================================

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=True,
    )

    # =========================================================
    # NOTIFICATION INFORMATION
    # =========================================================

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

    # =========================================================
    # NOTIFICATION STATUS
    # =========================================================

    status = Column(
        String(20),
        nullable=False,
        default="Unread",
    )

    # =========================================================
    # SCHEDULING / DELIVERY
    # =========================================================

    scheduled_at = Column(
        DateTime,
        nullable=True,
    )

    sent_at = Column(
        DateTime,
        nullable=True,
    )

    # =========================================================
    # READ INFORMATION
    # =========================================================

    read_at = Column(
        DateTime,
        nullable=True,
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =========================================================
    # USER RELATIONSHIP
    # =========================================================

    user = relationship(
        "User",
        back_populates="notifications",
    )

    # =========================================================
    # CONTRACT RELATIONSHIP
    # =========================================================

    contract = relationship(
        "Contract",
        back_populates="notifications",
    )

    # =========================================================
    # OBLIGATION RELATIONSHIP
    # =========================================================

    obligation = relationship(
        "Obligation",
        back_populates="notifications",
    )