from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
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

    version_number = Column(Integer, nullable=False)

    document_path = Column(String(500), nullable=True)

    change_summary = Column(Text, nullable=True)

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(DateTime, nullable=True)

    # Relationship with Contract
    contract = relationship(
        "Contract",
        back_populates="versions"
    )

    # Relationship with User
    creator = relationship(
        "User",
        back_populates="created_versions"
    )