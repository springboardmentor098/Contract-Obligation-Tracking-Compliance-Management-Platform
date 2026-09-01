import enum

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ObligationType(str, enum.Enum):
    PAYMENT = "Payment Obligation"
    DELIVERY = "Delivery Commitment"
    REPORTING = "Reporting Requirement"
    RENEWAL_CONDITION = "Renewal Condition"
    SLA = "Service Level Agreement"
    LEGAL_COMPLIANCE = "Legal Compliance Requirement"


class ObligationStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DELAYED = "Delayed"
    OVERDUE = "Overdue"


OBLIGATION_STATUS_TRANSITIONS = {
    ObligationStatus.PENDING: {ObligationStatus.IN_PROGRESS, ObligationStatus.COMPLETED, ObligationStatus.OVERDUE, ObligationStatus.DELAYED},
    ObligationStatus.IN_PROGRESS: {ObligationStatus.COMPLETED, ObligationStatus.DELAYED, ObligationStatus.OVERDUE},
    ObligationStatus.DELAYED: {ObligationStatus.IN_PROGRESS, ObligationStatus.COMPLETED, ObligationStatus.OVERDUE},
    ObligationStatus.OVERDUE: {ObligationStatus.IN_PROGRESS, ObligationStatus.COMPLETED},
    ObligationStatus.COMPLETED: set(),
}


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    obligation_type = Column(Enum(ObligationType), nullable=False)
    due_date = Column(Date, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ObligationStatus), nullable=False, default=ObligationStatus.PENDING)
    completion_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contract = relationship("Contract", back_populates="obligations")
    assignee = relationship("User", back_populates="obligations_assigned")
    notifications = relationship("Notification", back_populates="obligation")

    @property
    def is_overdue(self) -> bool:
        from datetime import date

        return self.status != ObligationStatus.COMPLETED and self.due_date < date.today()
