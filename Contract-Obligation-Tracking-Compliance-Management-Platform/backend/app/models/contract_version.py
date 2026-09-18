from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(Integer, ForeignKey("contracts.id"))

    version_number = Column(Integer, nullable=False)
    file_path = Column(String(255))
    change_summary = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="versions")