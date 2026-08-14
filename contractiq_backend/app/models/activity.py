from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        BigInteger,
        ForeignKey("contracts.id"),
        nullable=True
    )

    obligation_id = Column(
        BigInteger,
        ForeignKey("obligations.id"),
        nullable=True
    )

    activity_type = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    user = relationship(
        "User",
        backref="activities"
    )

    contract = relationship(
        "Contract",
        backref="activities"
    )

    obligation = relationship(
        "Obligation",
        backref="activities"
    )