from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    version_number = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    content_hash = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="versions"
    )