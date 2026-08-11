from sqlalchemy import Column, Date, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    party_name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    owner = relationship("User", back_populates="contracts")
    versions = relationship("ContractVersion", back_populates="contract")
    obligations = relationship("Obligation", back_populates="contract")
    renewals = relationship("Renewal", back_populates="contract")
    notifications = relationship("Notification", back_populates="contract")
    activities = relationship("Activity", back_populates="contract")