from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base
from app.models.contract import Contract
import enum
from sqlalchemy import Enum, Date, DateTime, Column, Integer, String, ForeignKey

# 1. USERS TABLE
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    contracts = relationship("Contract", back_populates="creator", foreign_keys="[Contract.created_by]")
    obligations = relationship("Obligation", back_populates="assignee")
    renewals = relationship("Renewal", back_populates="assignee")

# 3. CONTRACT VERSIONS TABLE
class ContractVersion(Base):
    __tablename__ = "contract_versions"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    version_number = Column(Integer, nullable=False)
    file_url = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="versions")

# 4. OBLIGATIONS TABLE
class ObligationType(str, enum.Enum):
    PAYMENT = "Payment Obligation"
    DELIVERY = "Delivery Commitment"
    REPORTING = "Reporting Requirement"
    RENEWAL = "Renewal Condition"
    SLA = "Service Level Agreement"
    LEGAL = "Legal Compliance Requirement"

class ObligationStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DELAYED = "Delayed"
    OVERDUE = "Overdue"

class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    obligation_type = Column(Enum(ObligationType, native_enum=False), nullable=False)
    due_date = Column(Date, nullable=False)
    
    # Link to the User responsible for it
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(ObligationStatus, native_enum=False), default=ObligationStatus.PENDING, nullable=False)
    completion_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (Make sure these match your User and Contract back_populates!)
    contract = relationship("Contract", back_populates="obligations")
    assignee = relationship("User", back_populates="obligations")



# 6. NOTIFICATIONS TABLE
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 7. REPORTS TABLE
class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    generated_by = Column(Integer, ForeignKey("users.id"))
    report_type = Column(String(100), nullable=False)
    file_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 8. AUDIT LOGS TABLE
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# 9. ACTIVITIES TABLE
class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action_description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# RENEWAL MODEL

class RenewalStatus(str, enum.Enum):
    UPCOMING = "Upcoming"
    IN_PROGRESS = "In Progress"
    RENEWED = "Renewed"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"

class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    renewal_date = Column(Date, nullable=False)
    previous_expiry_date = Column(Date, nullable=False)
    new_expiry_date = Column(Date, nullable=False)
    
    # native_enum=False prevents the PostgreSQL enum crash!
    status = Column(Enum(RenewalStatus, native_enum=False), default=RenewalStatus.UPCOMING, nullable=False)
    
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contract = relationship("Contract", back_populates="renewals")
    assignee = relationship("User", back_populates="renewals")

    # ==========================================
# SPRINT 11: COMPLIANCE MODEL
# ==========================================

class ComplianceStatusEnum(str, enum.Enum):
    COMPLIANT = "Compliant"
    PENDING = "Pending"
    DELAYED = "Delayed"
    NON_COMPLIANT = "Non-Compliant"
    HIGH_RISK = "High Risk"

class RiskLevelEnum(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    # native_enum=False saves us from PostgreSQL crashes!
    status = Column(Enum(ComplianceStatusEnum, native_enum=False), nullable=False)
    compliance_score = Column(Integer, nullable=False, default=0)
    risk_level = Column(Enum(RiskLevelEnum, native_enum=False), nullable=False, default=RiskLevelEnum.LOW)
    
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to the contract
    contract = relationship("Contract", back_populates="compliance_records")