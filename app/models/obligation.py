from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    obligation_type = Column(String(100), nullable=False)

    due_date = Column(Date, nullable=False)

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(String(50), nullable=False)

    compliance_status = Column(String(50), nullable=False)

    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship with Contract
    contract = relationship(
        "Contract",
        back_populates="obligations"
    )

    # Relationship with User
    assignee = relationship(
        "User",
        back_populates="obligations"
    )

    # Relationship with Notifications
    notifications = relationship(
        "Notification",
        back_populates="obligation"
    )