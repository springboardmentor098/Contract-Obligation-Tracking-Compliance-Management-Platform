from sqlalchemy import Column, DateTime, ForeignKey, Integer, BigInteger, String, Text
from sqlalchemy.orm import relationship
from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True
    )

    obligation_id = Column(
        Integer,
        ForeignKey("obligations.id"),
        nullable=True
    )

    activity_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="activities")
    contract = relationship("Contract", back_populates="activities")
    obligation = relationship("Obligation", back_populates="activities")