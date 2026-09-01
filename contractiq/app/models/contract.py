import enum

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ContractCategory(str, enum.Enum):
    EMPLOYMENT = "Employment Contract"
    VENDOR = "Vendor Contract"
    SERVICE_AGREEMENT = "Service Agreement"
    LEASE = "Lease Agreement"
    PURCHASE = "Purchase Agreement"
    PARTNERSHIP = "Partnership Agreement"
    CONFIDENTIALITY = "Confidentiality Agreement"


class ContractStatus(str, enum.Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    ACTIVE = "Active"
    EXPIRED = "Expired"
    TERMINATED = "Terminated"


# Allowed forward transitions for the contract lifecycle (Sprint 8)
CONTRACT_STATUS_TRANSITIONS = {
    ContractStatus.DRAFT: {ContractStatus.UNDER_REVIEW, ContractStatus.TERMINATED},
    ContractStatus.UNDER_REVIEW: {ContractStatus.APPROVED, ContractStatus.DRAFT, ContractStatus.TERMINATED},
    ContractStatus.APPROVED: {ContractStatus.ACTIVE, ContractStatus.TERMINATED},
    ContractStatus.ACTIVE: {ContractStatus.EXPIRED, ContractStatus.TERMINATED},
    ContractStatus.EXPIRED: set(),
    ContractStatus.TERMINATED: set(),
}


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(Enum(ContractCategory), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.DRAFT)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = relationship("User", back_populates="contracts_created", foreign_keys=[created_by])
    assignee = relationship("User", back_populates="contracts_assigned", foreign_keys=[assigned_to])

    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan")
    obligations = relationship("Obligation", back_populates="contract", cascade="all, delete-orphan")
    renewals = relationship("Renewal", back_populates="contract", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="contract")
