from sqlalchemy import Column, Integer, String, Date, DateTime, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    vendor_name = Column(String, nullable=False)
    contract_number = Column(String, unique=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, default="active")  # active, expired, terminated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    obligations = relationship(
        "Obligation", back_populates="contract", cascade="all, delete-orphan"
    )
