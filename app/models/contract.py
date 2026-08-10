from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    contract_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    category = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    start_date = Column(Date, nullable=False)

    end_date = Column(Date, nullable=True)

    status = Column(String(50), nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationship with User
    owner = relationship(
        "User",
        back_populates="contracts"
    )

    # Relationships with other tables
    versions = relationship(
        "ContractVersion",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    obligations = relationship(
        "Obligation",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    renewals = relationship(
        "Renewal",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="contract"
    )

    activities = relationship(
        "Activity",
        back_populates="contract"
    )