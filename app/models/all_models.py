from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

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
    contracts = relationship("Contract", back_populates="owner")
    obligations = relationship("Obligation", back_populates="assignee")

# 2. CONTRACTS TABLE
class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="contracts")
    versions = relationship("ContractVersion", back_populates="contract")
    obligations = relationship("Obligation", back_populates="contract")
    renewal = relationship("Renewal", back_populates="contract", uselist=False) # 1-to-1

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
class Obligation(Base):
    __tablename__ = "obligations"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    description = Column(Text, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))

    contract = relationship("Contract", back_populates="obligations")
    assignee = relationship("User", back_populates="obligations")

# 5. RENEWALS TABLE
class Renewal(Base):
    __tablename__ = "renewals"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), unique=True) # Unique for 1-to-1
    renewal_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    reminder_days = Column(Integer, nullable=False)

    contract = relationship("Contract", back_populates="renewal")

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