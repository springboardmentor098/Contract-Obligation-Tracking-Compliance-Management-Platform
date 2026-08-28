from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    version_number = Column(Integer)
    file_path = Column(String(255))
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    contract = relationship("Contract", back_populates="contract_versions")