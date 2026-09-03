from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # USER WHO RECEIVES THE NOTIFICATION
    # ============================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ============================================================
    # RELATED CONTRACT
    # Optional because some notifications may not be contract-specific
    # ============================================================

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True
    )

    # ============================================================
    # RELATED OBLIGATION
    # Optional because not every notification is obligation-related
    # ============================================================

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=True
    )

    # ============================================================
    # NOTIFICATION TYPE
    #
    # Renewal Reminder
    # Obligation Due Alert
    # Obligation Overdue Alert
    # Compliance Alert
    # Contract Approval Alert
    # Contract Status Alert
    # ============================================================

    notification_type = Column(
        String(100),
        nullable=False
    )

    # ============================================================
    # NOTIFICATION TITLE
    # ============================================================

    title = Column(
        String(255),
        nullable=False
    )

    # ============================================================
    # NOTIFICATION MESSAGE
    # ============================================================

    message = Column(
        Text,
        nullable=False
    )

    # ============================================================
    # NOTIFICATION STATUS
    #
    # Unread
    # Read
    # ============================================================

    status = Column(
        String(20),
        nullable=False,
        default="Unread"
    )

    # ============================================================
    # SCHEDULED TIME
    # ============================================================

    scheduled_at = Column(
        DateTime,
        nullable=True
    )

    # ============================================================
    # SENT TIME
    # ============================================================

    sent_at = Column(
        DateTime,
        nullable=True
    )

    # ============================================================
    # READ TIME
    # ============================================================

    read_at = Column(
        DateTime,
        nullable=True
    )

    # ============================================================
    # SYSTEM TIMESTAMPS
    # ============================================================

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ============================================================
    # USER RELATIONSHIP
    # ============================================================

    user = relationship(
        "User",
        back_populates="notifications"
    )

    # ============================================================
    # CONTRACT RELATIONSHIP
    # ============================================================

    contract = relationship(
        "Contract",
        back_populates="notifications"
    )

    # ============================================================
    # OBLIGATION RELATIONSHIP
    # ============================================================

    obligation = relationship(
        "Obligation",
        back_populates="notifications"
    )