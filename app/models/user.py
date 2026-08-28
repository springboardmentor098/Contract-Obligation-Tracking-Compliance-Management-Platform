from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    password = Column(String, nullable=False)

    contracts = relationship(
    "Contract",
    foreign_keys="Contract.created_by",
    back_populates="owner"
    )
    obligations = relationship(
        "Obligation",
        back_populates="assigned_user"
    )
    
    renewals = relationship(
    "Renewal",
    back_populates="assigned_user"
    )

    notifications = relationship(
        "Notification",
        back_populates="user"
    )

    reports = relationship(
        "Report",
        back_populates="generated_by_user"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    activities = relationship(
        "Activity",
        back_populates="user"
    )