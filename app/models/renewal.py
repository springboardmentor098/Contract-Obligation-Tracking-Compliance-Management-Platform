import enum

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RenewalStatus(str, enum.Enum):
    UPCOMING = "Upcoming"
    IN_PROGRESS = "In Progress"
    RENEWED = "Renewed"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"


RENEWAL_STATUS_TRANSITIONS = {
    RenewalStatus.UPCOMING: {RenewalStatus.IN_PROGRESS, RenewalStatus.EXPIRED, RenewalStatus.CANCELLED},
    RenewalStatus.IN_PROGRESS: {RenewalStatus.RENEWED, RenewalStatus.CANCELLED},
    RenewalStatus.RENEWED: set(),
    RenewalStatus.EXPIRED: set(),
    RenewalStatus.CANCELLED: set(),
}


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    renewal_date = Column(Date, nullable=False)
    previous_expiry_date = Column(Date, nullable=False)
    new_expiry_date = Column(Date, nullable=False)
    status = Column(Enum(RenewalStatus), nullable=False, default=RenewalStatus.UPCOMING)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contract = relationship("Contract", back_populates="renewals")
    assignee = relationship("User", back_populates="renewals_assigned")
