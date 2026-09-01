import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class NotificationType(str, enum.Enum):
    RENEWAL_REMINDER = "Renewal Reminder"
    OBLIGATION_DUE_ALERT = "Obligation Due Alert"
    OBLIGATION_OVERDUE_ALERT = "Obligation Overdue Alert"
    COMPLIANCE_ALERT = "Compliance Alert"
    CONTRACT_APPROVAL_ALERT = "Contract Approval Alert"
    CONTRACT_STATUS_ALERT = "Contract Status Alert"


class NotificationStatus(str, enum.Enum):
    UNREAD = "Unread"
    READ = "Read"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    obligation_id = Column(Integer, ForeignKey("obligations.id"), nullable=True)

    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), nullable=False, default=NotificationStatus.UNREAD)

    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="notifications")
    contract = relationship("Contract", back_populates="notifications")
    obligation = relationship("Obligation", back_populates="notifications")
