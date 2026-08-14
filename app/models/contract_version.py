from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class ContractVersion(Base):
    __tablename__ = "contract_versions"

    version_id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.contract_id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_url = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)
