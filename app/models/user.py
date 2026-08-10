from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    contracts = relationship("Contract", back_populates="created_by_user")
    notifications = relationship("Notification", back_populates="user")
    reports = relationship("Report", back_populates="generated_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")
    activities = relationship("Activity", back_populates="user")