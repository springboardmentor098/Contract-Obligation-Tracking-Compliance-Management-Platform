from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    contract_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    contract_type = Column(String(50), nullable=False)
    counterparty_name = Column(String(150), nullable=False)
    status = Column(String(30), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    contract_value = Column(Numeric(14, 2), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    current_version_id = Column(
        Integer,
        ForeignKey("contract_versions.version_id", use_alter=True, name="fk_contracts_current_version_id"),
        nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
