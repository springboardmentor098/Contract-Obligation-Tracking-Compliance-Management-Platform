from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, func
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

    title = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    obligation_type = Column(String(100), nullable=False)

    due_date = Column(Date, nullable=False)

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="Pending"
    )

    completion_date = Column(Date, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="obligations"
    )

    assigned_to_user = relationship(
        "User",
        back_populates="assigned_obligations",
        foreign_keys=[assigned_to]
    )