from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    version_number = Column(
        Integer,
        nullable=False
    )

    document_path = Column(
        String(500),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="versions"
    )

    creator = relationship(
        "User",
        back_populates="contract_versions"
    )