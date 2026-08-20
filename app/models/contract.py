from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.database import Base 

# 1. Define Categories
class ContractCategory(str, enum.Enum):
    EMPLOYMENT = "Employment Contract"
    VENDOR = "Vendor Contract"
    SERVICE = "Service Agreement"
    LEASE = "Lease Agreement"
    PURCHASE = "Purchase Agreement"
    PARTNERSHIP = "Partnership Agreement"
    CONFIDENTIALITY = "Confidentiality Agreement"

# 2. Define Statuses
class ContractStatus(str, enum.Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    ACTIVE = "Active"
    EXPIRED = "Expired"
    TERMINATED = "Terminated"

# 3. Define the Database Table
class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    contract_number = Column(String, unique=True, index=True, nullable=False)
    category = Column(Enum(ContractCategory), nullable=False)
    description = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT, nullable=False)
    
    # Link to the User who created it
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Relationship to fetch the user easily later
    creator = relationship("User", foreign_keys=[created_by], back_populates="contracts")
    versions = relationship("ContractVersion", back_populates="contract")
    assignee = relationship("User", foreign_keys=[assigned_to])

    obligations = relationship("Obligation")
    renewal = relationship("Renewal", uselist=False)