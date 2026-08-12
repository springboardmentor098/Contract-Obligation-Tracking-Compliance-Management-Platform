from sqlalchemy import Column, Integer, Text, ForeignKey
from app.database.database import Base

class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    version_no = Column(Integer, nullable=False)
    file_path = Column(Text, nullable=False)
    