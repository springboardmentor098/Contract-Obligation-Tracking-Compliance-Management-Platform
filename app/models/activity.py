from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True
    )

    activity_type = Column(String(100), nullable=False)

    description = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship with User
    user = relationship(
        "User",
        back_populates="activities"
    )

    # Relationship with Contract
    contract = relationship(
        "Contract",
        back_populates="activities"
    )