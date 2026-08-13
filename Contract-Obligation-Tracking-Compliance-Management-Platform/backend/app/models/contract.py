from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String(200), nullable=False)
    contract_number = Column(String(100), unique=True, nullable=False)
    vendor_name = Column(String(200), nullable=False)
    description = Column(Text)

    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="Active")

    owner_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="contracts")

    versions = relationship("ContractVersion", back_populates="contract")
    obligations = relationship("Obligation", back_populates="contract")