from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
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

    due_date = Column(Date, nullable=True)

    status = Column(String(50), nullable=True)

    priority = Column(String(50), nullable=True)

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(DateTime, nullable=True)

    updated_at = Column(DateTime, nullable=True)

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